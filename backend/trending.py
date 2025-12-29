"""
OpenRouter trending models updater.
Fetches Top Weekly models and updates documentation tables marked with
BEGIN/END markers, and persists raw data for use in provider selection.
"""
import os
import json
import logging
import re
from typing import List, Dict

import requests

from backend.config import Config

logger = logging.getLogger(__name__)

MARKER_BEGIN = "<!-- BEGIN: OPENROUTER_TOP_WEEKLY -->"
MARKER_END = "<!-- END: OPENROUTER_TOP_WEEKLY -->"


def fetch_openrouter_top_weekly(url: str = None) -> List[Dict]:
    """Fetch OpenRouter Top Weekly models (JSON).

    Returns a list of records with fields like `id`, `name`, `provider`,
    `weekly_tokens` if available. If the schema differs, we map best-effort.
    """
    feed_url = url or Config.OPENROUTER_TREND_URL
    try:
        resp = requests.get(feed_url, timeout=30, headers={"Accept": "application/json, text/plain; q=0.9, */*;q=0.8"})
        resp.raise_for_status()
        try:
            data = resp.json()
            return _normalize_openrouter_json(data)
        except Exception:
            pass

        # Try CSV
        csv_url = feed_url.replace('fmt=json', 'fmt=csv')
        resp_csv = requests.get(csv_url, timeout=30)
        if resp_csv.ok and ',' in resp_csv.text:
            return _parse_csv(resp_csv.text)

        # Try table (markdown)
        table_url = feed_url.replace('fmt=json', 'fmt=table')
        resp_tbl = requests.get(table_url, timeout=30)
        if resp_tbl.ok:
            return _parse_markdown_table(resp_tbl.text)

        return []
    except Exception as e:
        logger.error(f"Failed to fetch OpenRouter Top Weekly: {e}")
        return []


def _normalize_openrouter_json(data) -> List[Dict]:
    items = []
    if isinstance(data, dict) and 'data' in data:
        raw_items = data['data']
    elif isinstance(data, list):
        raw_items = data
    else:
        raw_items = []

    for idx, item in enumerate(raw_items, start=1):
        name = item.get('name') or item.get('id') or item.get('model') or 'unknown'
        provider = item.get('provider') or item.get('org') or item.get('vendor') or 'unknown'
        weekly_tokens = item.get('weekly_tokens') or item.get('popularity') or item.get('tokens_weekly')
        items.append({
            'rank': idx,
            'name': name,
            'provider': provider,
            'weekly_tokens': weekly_tokens,
        })
    return items


def _parse_csv(text: str) -> List[Dict]:
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return []
    header = [h.strip().lower() for h in lines[0].split(',')]
    def idx(col):
        try:
            return header.index(col)
        except ValueError:
            return -1
    i_name = idx('name') if 'name' in header else idx('model')
    i_prov = idx('provider') if 'provider' in header else idx('org')
    i_week = idx('weekly_tokens') if 'weekly_tokens' in header else idx('tokens_weekly')
    items: List[Dict] = []
    for rank, row in enumerate(lines[1:], start=1):
        cols = [c.strip() for c in row.split(',')]
        name = cols[i_name] if i_name >= 0 and i_name < len(cols) else 'unknown'
        provider = cols[i_prov] if i_prov >= 0 and i_prov < len(cols) else 'unknown'
        weekly_raw = cols[i_week] if i_week >= 0 and i_week < len(cols) else ''
        try:
            weekly = int(weekly_raw)
        except Exception:
            weekly = None
        items.append({'rank': rank, 'name': name, 'provider': provider, 'weekly_tokens': weekly})
    return items


def _parse_markdown_table(text: str) -> List[Dict]:
    items: List[Dict] = []
    lines = [l.strip() for l in text.splitlines()]
    # Find rows starting with | and having at least 4 columns
    table_rows = [l for l in lines if l.startswith('|')]
    # Skip header and separator lines
    data_rows = [l for l in table_rows if not (set(l.replace('|', '').strip()) <= set('-: '))]
    rank = 0
    for l in data_rows:
        cols = [c.strip() for c in l.strip('|').split('|')]
        if len(cols) < 3:
            continue
        # Try to map: #, Model/Name, Provider
        try:
            maybe_rank = int(cols[0])
            rank = maybe_rank
        except Exception:
            rank += 1
        name = cols[1] if len(cols) > 1 else 'unknown'
        provider = cols[2] if len(cols) > 2 else 'unknown'
        weekly = None
        # If a 4th column exists, may hold tokens
        if len(cols) > 3:
            try:
                weekly = int(cols[3].replace(',', '').split()[0])
            except Exception:
                weekly = None
        items.append({'rank': rank, 'name': name, 'provider': provider, 'weekly_tokens': weekly})
    return items


def format_markdown_table(items: List[Dict], limit: int = 20) -> str:
    """Build markdown table string for trending models.
    Columns: # | Model | Provider | Weekly Tokens
    """
    rows = ["| # | Model | Provider | Weekly Tokens |", "|---|--------------------------|-----------|----------------|"]
    for rec in items[:limit]:
        rank = rec.get('rank')
        name = rec.get('name') or '—'
        provider = rec.get('provider') or '—'
        weekly = rec.get('weekly_tokens')
        weekly_str = f"{weekly:,}" if isinstance(weekly, (int, float)) else "—"
        rows.append(f"| {rank} | {name} | {provider} | {weekly_str} |")
    return "\n".join(rows)


def update_doc_file(path: str, table_md: str) -> bool:
    """Replace the block between markers with the given table.
    Returns True if file updated, False otherwise.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        pattern = re.compile(re.escape(MARKER_BEGIN) + r"[\s\S]*?" + re.escape(MARKER_END))
        new_block = f"{MARKER_BEGIN}\n{table_md}\n{MARKER_END}"

        if re.search(pattern, content):
            new_content = re.sub(pattern, new_block, content)
        else:
            # If markers missing, append block at end
            new_content = content.rstrip() + "\n\n" + new_block + "\n"

        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info(f"Updated trending table in {path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to update {path}: {e}")
        return False


def persist_json(items: List[Dict], out_path: str = None) -> None:
    """Persist fetched items to data/trending_models.json."""
    target = out_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'trending_models.json')
    os.makedirs(os.path.dirname(target), exist_ok=True)
    try:
        with open(target, 'w', encoding='utf-8') as f:
            json.dump({'source': Config.OPENROUTER_TREND_URL, 'items': items}, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved trending data to {target}")
    except Exception as e:
        logger.error(f"Failed to save trending data: {e}")


def update_openrouter_top_weekly(doc_paths: List[str] = None) -> bool:
    """Fetch trending models and update docs.

    Args:
        doc_paths: list of documentation files to update.
    Returns:
        True if at least one file updated.
    """
    items = fetch_openrouter_top_weekly()
    if not items:
        logger.warning("No trending items fetched; skipping doc update")
        return False

    table_md = format_markdown_table(items)

    # Default docs to update
    paths = doc_paths or [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', 'LLMs.md'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', 'openrouter.md'),
    ]

    any_updated = False
    for p in paths:
        if update_doc_file(p, table_md):
            any_updated = True

    persist_json(items)
    return any_updated


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    updated = update_openrouter_top_weekly()
    print("Updated:" if updated else "No changes.")

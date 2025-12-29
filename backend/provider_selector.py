"""
Dynamic provider selector with trend_score support.
Combines estimated cost, latency, quality, and OpenRouter weekly popularity.
"""
import json
import os
from typing import Dict, Optional


class DynamicProviderSelector:
    """Select models using weighted scoring.

    Score = w_quality*quality + w_cost*(1/cost) + w_speed*(1/latency)
            + w_trend*trend_score

    - `quality`, `latency` can be provided heuristically or from telemetry.
    - `trend_score` is normalized weekly tokens from OpenRouter feed.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {
            'quality': 0.4,
            'cost': 0.3,
            'speed': 0.1,
            'trend': 0.2,
        }
        self.trending = self._load_trending()

    def _load_trending(self) -> Dict[str, float]:
        """Load data/trending_models.json and build model->trend_score mapping."""
        base = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base, 'data', 'trending_models.json')
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            items = data.get('items', [])
            # Normalize model name to lowercase key
            scores = {}
            max_tokens = 0
            for item in items:
                wt = item.get('weekly_tokens')
                if isinstance(wt, (int, float)):
                    max_tokens = max(max_tokens, wt)
            # Prevent division by zero
            denom = max_tokens or 1
            for item in items:
                name = str(item.get('name') or '').lower()
                wt = item.get('weekly_tokens')
                norm = (wt / denom) if isinstance(wt, (int, float)) else 0.0
                scores[name] = norm
            return scores
        except Exception:
            return {}

    def score(self, *, model: str, cost_per_1k: float, quality: float = 0.5, latency_ms: float = 500.0) -> float:
        """Compute the score for a model.
        - `model`: model identifier string
        - `cost_per_1k`: dollars per 1K tokens
        - `quality`: 0..1 heuristic
        - `latency_ms`: response latency in ms
        """
        w = self.weights
        inv_cost = 1.0 / max(cost_per_1k, 1e-9)
        inv_latency = 1.0 / max(latency_ms, 1e-3)
        trend = self.trending.get(model.lower(), 0.0)
        return (
            w['quality'] * quality +
            w['cost'] * inv_cost +
            w['speed'] * inv_latency +
            w['trend'] * trend
        )

    def choose(self, candidates: Dict[str, Dict]) -> str:
        """Choose best model from candidates.
        `candidates` map: model -> {cost_per_1k, quality, latency_ms}
        Returns the model name with highest score.
        """
        best_model = None
        best_score = float('-inf')
        for model, meta in candidates.items():
            s = self.score(
                model=model,
                cost_per_1k=float(meta.get('cost_per_1k', 0.001)),
                quality=float(meta.get('quality', 0.5)),
                latency_ms=float(meta.get('latency_ms', 500.0)),
            )
            if s > best_score:
                best_score = s
                best_model = model
        return best_model or list(candidates.keys())[0]

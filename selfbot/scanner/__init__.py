"""
Opportunity Scanner module for SelfEarnBot.
"""
from .base import BaseScanner
from .rss_monitor import RSSScanner
from .freelance import FreelanceScanner
from .content_markets import ContentMarketScanner

__all__ = [
    'BaseScanner',
    'RSSScanner',
    'FreelanceScanner',
    'ContentMarketScanner'
]

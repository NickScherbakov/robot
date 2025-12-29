"""
RSS Feed Monitor for finding content opportunities.
Monitors RSS feeds for content requests and opportunities.
"""
from .base import BaseScanner
from typing import List, Dict
import feedparser
import logging
import random

logger = logging.getLogger(__name__)


class RSSScanner(BaseScanner):
    """Scans RSS feeds for content opportunities"""
    
    def __init__(self, feed_urls: List[str] = None):
        super().__init__("RSSScanner")
        self.feed_urls = feed_urls or []
        logger.info(f"RSS Scanner initialized with {len(self.feed_urls)} feeds")
    
    def scan(self) -> List[Dict]:
        """
        Scan RSS feeds for opportunities.
        
        Returns:
            List of opportunities found in feeds
        """
        opportunities = []
        
        if not self.feed_urls:
            # Demo mode: Generate mock opportunities
            logger.info("No RSS feeds configured, generating demo opportunities")
            return self._generate_demo_opportunities()
        
        for feed_url in self.feed_urls:
            try:
                logger.info(f"Scanning RSS feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Limit to 10 entries per feed
                    opportunity = self._parse_entry(entry, feed_url)
                    if opportunity:
                        opportunities.append(opportunity)
                        
            except Exception as e:
                logger.error(f"Error scanning RSS feed {feed_url}: {e}")
        
        logger.info(f"Found {len(opportunities)} opportunities from RSS feeds")
        return opportunities
    
    def _parse_entry(self, entry, feed_url: str) -> Dict:
        """Parse RSS entry into opportunity"""
        # Extract relevant information
        title = getattr(entry, 'title', 'Untitled')
        description = getattr(entry, 'summary', '')
        link = getattr(entry, 'link', feed_url)
        
        # Determine content type based on keywords
        content_type = self._determine_content_type(title, description)
        
        # Estimate revenue based on content type
        estimated_revenue = self._estimate_revenue(content_type)
        
        return {
            'source': 'rss',
            'source_url': link,
            'title': title,
            'description': description[:500],  # Limit description length
            'content_type': content_type,
            'estimated_revenue': estimated_revenue,
            'requirements': {
                'original_feed': feed_url,
                'keywords': self._extract_keywords(title, description)
            }
        }
    
    def _determine_content_type(self, title: str, description: str) -> str:
        """Determine content type from title and description"""
        text = (title + ' ' + description).lower()
        
        if any(kw in text for kw in ['article', 'blog', 'post', 'write']):
            return 'article'
        elif any(kw in text for kw in ['code', 'script', 'program', 'develop']):
            return 'code'
        elif any(kw in text for kw in ['seo', 'description', 'meta']):
            return 'seo_content'
        else:
            return 'article'  # Default
    
    def _estimate_revenue(self, content_type: str) -> float:
        """Estimate revenue based on content type"""
        from selfbot.config import SelfBotConfig
        
        economics = SelfBotConfig.ECONOMICS.get(content_type, {})
        min_rev = economics.get('revenue_min', 5.0)
        max_rev = economics.get('revenue_max', 20.0)
        
        # Random estimate within range
        return round(random.uniform(min_rev, max_rev), 2)
    
    def _extract_keywords(self, title: str, description: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction (in production, use NLP)
        text = (title + ' ' + description).lower()
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = text.split()
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        return keywords[:10]  # Top 10 keywords
    
    def _generate_demo_opportunities(self) -> List[Dict]:
        """Generate demo opportunities for testing"""
        demo_opportunities = [
            {
                'source': 'rss_demo',
                'source_url': 'https://example.com/content-needed',
                'title': 'Need article about AI trends in 2025',
                'description': 'Looking for a comprehensive article discussing the latest AI trends, including LLMs, computer vision, and automation.',
                'content_type': 'article',
                'estimated_revenue': 25.00,
                'requirements': {
                    'word_count': 1000,
                    'keywords': ['AI', 'trends', 'machine learning', 'automation']
                }
            },
            {
                'source': 'rss_demo',
                'source_url': 'https://example.com/seo-content',
                'title': 'SEO product descriptions needed',
                'description': 'Need SEO-optimized product descriptions for tech gadgets.',
                'content_type': 'seo_content',
                'estimated_revenue': 15.00,
                'requirements': {
                    'word_count': 300,
                    'keywords': ['tech', 'gadgets', 'innovative']
                }
            },
            {
                'source': 'rss_demo',
                'source_url': 'https://example.com/code-help',
                'title': 'Python script for data processing',
                'description': 'Need a simple Python script to process CSV files and generate reports.',
                'content_type': 'code',
                'estimated_revenue': 40.00,
                'requirements': {
                    'language': 'python',
                    'keywords': ['data processing', 'CSV', 'reports']
                }
            }
        ]
        
        # Randomly select 1-2 opportunities
        num_opps = random.randint(1, 2)
        return random.sample(demo_opportunities, num_opps)

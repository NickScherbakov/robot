"""
Earning strategies for different opportunity types.
"""
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class EarningStrategy:
    """Defines strategies for different earning opportunities"""
    
    def __init__(self):
        self.strategies = {
            'article': self._article_strategy,
            'code': self._code_strategy,
            'seo_content': self._seo_strategy
        }
        logger.info("EarningStrategy initialized")
    
    def get_strategy(self, opportunity: Dict) -> Dict:
        """
        Get the best strategy for an opportunity.
        
        Args:
            opportunity: Opportunity dictionary
            
        Returns:
            Strategy dictionary with execution plan
        """
        content_type = opportunity.get('content_type', 'article')
        strategy_func = self.strategies.get(content_type, self._default_strategy)
        
        return strategy_func(opportunity)
    
    def _article_strategy(self, opportunity: Dict) -> Dict:
        """Strategy for article opportunities"""
        requirements = opportunity.get('requirements', {})
        
        return {
            'content_type': 'article',
            'ai_provider': 'mistral',  # Cheaper for articles
            'generation_params': {
                'word_count': requirements.get('word_count', 800),
                'tone': 'professional',
                'keywords': requirements.get('keywords', [])
            },
            'publisher': 'platform',
            'estimated_time_minutes': 5,
            'confidence': 0.85
        }
    
    def _code_strategy(self, opportunity: Dict) -> Dict:
        """Strategy for code opportunities"""
        requirements = opportunity.get('requirements', {})
        
        return {
            'content_type': 'code',
            'ai_provider': 'openai',  # Better for code
            'generation_params': {
                'language': requirements.get('language', 'python'),
                'description': opportunity.get('title', ''),
                'keywords': requirements.get('keywords', [])
            },
            'publisher': 'freelance',
            'estimated_time_minutes': 8,
            'confidence': 0.75
        }
    
    def _seo_strategy(self, opportunity: Dict) -> Dict:
        """Strategy for SEO content opportunities"""
        requirements = opportunity.get('requirements', {})
        
        return {
            'content_type': 'seo_content',
            'ai_provider': 'mistral',  # Cheap and effective for SEO
            'generation_params': {
                'word_count': requirements.get('word_count', 300),
                'tone': 'persuasive',
                'keywords': requirements.get('keywords', [])
            },
            'publisher': 'freelance',
            'estimated_time_minutes': 3,
            'confidence': 0.90
        }
    
    def _default_strategy(self, opportunity: Dict) -> Dict:
        """Default strategy for unknown types"""
        return {
            'content_type': 'article',
            'ai_provider': 'mistral',
            'generation_params': {
                'word_count': 500,
                'tone': 'professional'
            },
            'publisher': 'platform',
            'estimated_time_minutes': 5,
            'confidence': 0.6
        }
    
    def optimize_provider_selection(self, content_type: str, budget: float) -> str:
        """
        Select best AI provider based on budget and content type.
        
        Args:
            content_type: Type of content to generate
            budget: Available budget
            
        Returns:
            Provider name ('openai' or 'mistral')
        """
        # If budget is very low, always use mistral
        if budget < 0.01:
            return 'mistral'
        
        # For code, prefer OpenAI if budget allows
        if content_type == 'code' and budget >= 0.02:
            return 'openai'
        
        # For most content, mistral is cost-effective
        return 'mistral'

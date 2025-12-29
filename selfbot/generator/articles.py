"""
Article generator using AI APIs.
Generates blog posts, articles, and written content.
"""
from .base import BaseGenerator
from typing import Dict
from backend.ai_providers import AIManager
import logging

logger = logging.getLogger(__name__)


class ArticleGenerator(BaseGenerator):
    """Generates articles and blog posts"""
    
    def __init__(self, ai_manager: AIManager = None):
        super().__init__("ArticleGenerator")
        self.ai_manager = ai_manager or AIManager()
    
    def generate(self, requirements: Dict) -> Dict:
        """
        Generate an article based on requirements.
        
        Args:
            requirements: Dict with keys:
                - title or topic: Article topic
                - keywords: List of keywords to include
                - word_count: Target word count (default: 800)
                - tone: Writing tone (default: professional)
                - ai_provider: AI provider to use (default: mistral)
                
        Returns:
            Generated article data
        """
        if not self.validate_requirements(requirements):
            raise ValueError("Invalid requirements for article generation")
        
        # Extract requirements
        topic = requirements.get('title') or requirements.get('topic', 'General Topic')
        keywords = requirements.get('keywords', [])
        word_count = requirements.get('word_count', 800)
        tone = requirements.get('tone', 'professional')
        ai_provider = requirements.get('ai_provider', 'mistral')
        
        # Build prompt
        prompt = self._build_article_prompt(topic, keywords, word_count, tone)
        
        logger.info(f"Generating article: '{topic}' (~{word_count} words)")
        
        try:
            # Generate using AI
            result = self.ai_manager.execute_task(
                prompt=prompt,
                provider=ai_provider,
                max_tokens=min(word_count * 2, 2000)  # Rough token estimate
            )
            
            # Assess quality
            quality_score = self._assess_quality(result['response'], word_count, keywords)
            
            return {
                'content': result['response'],
                'title': topic,
                'tokens_used': result['tokens_used'],
                'cost': result['cost'],
                'quality_score': quality_score,
                'metadata': {
                    'ai_provider': ai_provider,
                    'word_count': len(result['response'].split()),
                    'keywords_included': self._count_keywords(result['response'], keywords)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating article: {e}")
            raise
    
    def _build_article_prompt(self, topic: str, keywords: list, word_count: int, tone: str) -> str:
        """Build prompt for article generation"""
        keywords_str = ', '.join(keywords[:5]) if keywords else ''
        
        prompt = f"""Write a {tone} article about: {topic}

Requirements:
- Length: approximately {word_count} words
- Include relevant examples and insights
- Make it engaging and informative
"""
        
        if keywords_str:
            prompt += f"- Include these keywords naturally: {keywords_str}\n"
        
        prompt += "\nArticle:"
        
        return prompt
    
    def _assess_quality(self, content: str, target_word_count: int, keywords: list) -> float:
        """
        Self-assess content quality.
        
        Returns:
            Quality score between 0 and 1
        """
        score = 0.5  # Base score
        
        # Check word count (closer to target = higher score)
        actual_word_count = len(content.split())
        word_count_ratio = min(actual_word_count / target_word_count, 1.0)
        if word_count_ratio > 0.7:  # At least 70% of target
            score += 0.2
        
        # Check keyword inclusion
        if keywords:
            keywords_found = self._count_keywords(content, keywords)
            keyword_ratio = keywords_found / len(keywords)
            score += keyword_ratio * 0.2
        
        # Check minimum length
        if actual_word_count > 100:
            score += 0.1
        
        return min(score, 1.0)
    
    def _count_keywords(self, content: str, keywords: list) -> int:
        """Count how many keywords are present in content"""
        content_lower = content.lower()
        return sum(1 for kw in keywords if kw.lower() in content_lower)
    
    def estimate_cost(self, requirements: Dict) -> float:
        """Estimate cost for article generation"""
        word_count = requirements.get('word_count', 800)
        ai_provider = requirements.get('ai_provider', 'mistral')
        
        # Estimate tokens (roughly 1.3 tokens per word for English)
        estimated_tokens = word_count * 1.3
        
        # Cost per 1K tokens
        cost_rates = {
            'mistral': 0.0002,  # Mistral-tiny
            'openai': 0.00015,   # GPT-4o-mini
            'mistral': 0.0002,   # Mistral-small
        }
        
        cost_per_1k = cost_rates.get(ai_provider, 0.002)
        estimated_cost = (estimated_tokens / 1000) * cost_per_1k
        
        return round(estimated_cost, 4)

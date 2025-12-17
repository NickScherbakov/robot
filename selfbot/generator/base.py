"""
Base generator class for content creation.
All content generators should inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseGenerator(ABC):
    """Base class for all content generators"""
    
    def __init__(self, name: str, ai_provider=None):
        self.name = name
        self.ai_provider = ai_provider
        logger.info(f"Initialized generator: {name}")
    
    @abstractmethod
    def generate(self, requirements: Dict) -> Dict:
        """
        Generate content based on requirements.
        
        Args:
            requirements: Dictionary with content requirements
            
        Returns:
            Dictionary with:
            - content: Generated content
            - title: Content title
            - tokens_used: Number of tokens consumed
            - cost: Generation cost in USD
            - quality_score: Self-assessed quality (0-1)
            - metadata: Additional metadata
        """
        pass
    
    def estimate_cost(self, requirements: Dict) -> float:
        """
        Estimate cost of generating content.
        
        Args:
            requirements: Content requirements
            
        Returns:
            Estimated cost in USD
        """
        # Default estimation based on word count
        word_count = requirements.get('word_count', 500)
        # Rough estimate: ~750 tokens per 500 words, $0.002 per 1K tokens
        estimated_tokens = (word_count / 500) * 750
        estimated_cost = (estimated_tokens / 1000) * 0.002
        return round(estimated_cost, 4)
    
    def validate_requirements(self, requirements: Dict) -> bool:
        """
        Validate that requirements are sufficient.
        
        Args:
            requirements: Requirements dictionary
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - can be overridden
        return isinstance(requirements, dict)

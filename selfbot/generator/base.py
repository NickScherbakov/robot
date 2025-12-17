"""
Base generator class for content creation.
All content generators should inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Cost estimation constants
DEFAULT_WORDS_PER_TOKEN = 0.75  # Rough estimate: ~750 tokens per 500 words
DEFAULT_COST_PER_1K_TOKENS = 0.002  # Default cost (Mistral-tiny rate)


class BaseGenerator(ABC):
    """Base class for all content generators"""
    
    def __init__(self, name: str):
        """
        Initialize base generator.
        
        Args:
            name: Generator name for logging
        """
        self.name = name
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
        # Estimate tokens based on word count
        estimated_tokens = word_count * DEFAULT_WORDS_PER_TOKEN
        estimated_cost = (estimated_tokens / 1000) * DEFAULT_COST_PER_1K_TOKENS
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

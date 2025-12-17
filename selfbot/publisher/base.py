"""
Base publisher class for content submission.
All publishers should inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class BasePublisher(ABC):
    """Base class for all content publishers"""
    
    def __init__(self, name: str):
        self.name = name
        logger.info(f"Initialized publisher: {name}")
    
    @abstractmethod
    def publish(self, content: Dict, opportunity: Dict) -> Dict:
        """
        Publish/submit content.
        
        Args:
            content: Generated content dictionary
            opportunity: Original opportunity dictionary
            
        Returns:
            Dictionary with:
            - status: submission status
            - platform_url: URL if published
            - message: Status message
            - estimated_revenue: Expected revenue
        """
        pass
    
    def validate_content(self, content: Dict) -> bool:
        """Validate content before publishing"""
        return (
            content.get('content') and
            content.get('title') and
            content.get('quality_score', 0) > 0.5
        )

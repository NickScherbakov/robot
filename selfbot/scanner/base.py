"""
Base scanner class for opportunity detection.
All scanners should inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class BaseScanner(ABC):
    """Base class for all opportunity scanners"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        logger.info(f"Initialized scanner: {name}")
    
    @abstractmethod
    def scan(self) -> List[Dict]:
        """
        Scan for opportunities.
        
        Returns:
            List of opportunity dictionaries with keys:
            - source: Scanner source identifier
            - source_url: URL if available
            - title: Opportunity title
            - description: Description
            - content_type: Type of content needed
            - estimated_revenue: Estimated revenue in USD
            - requirements: Additional requirements dict
        """
        pass
    
    def is_enabled(self) -> bool:
        """Check if scanner is enabled"""
        return self.enabled
    
    def enable(self):
        """Enable the scanner"""
        self.enabled = True
        logger.info(f"Enabled scanner: {self.name}")
    
    def disable(self):
        """Disable the scanner"""
        self.enabled = False
        logger.info(f"Disabled scanner: {self.name}")

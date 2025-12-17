"""
Helper utilities for SelfEarnBot.
"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def format_currency(amount: float, currency: str = 'USD') -> str:
    """
    Format amount as currency.
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted string
    """
    symbol = {'USD': '$', 'EUR': '€', 'GBP': '£'}.get(currency, '$')
    return f"{symbol}{amount:.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format value as percentage.
    
    Args:
        value: Value to format (e.g., 0.5 for 50%)
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    return f"{value * 100:.{decimals}f}%"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Result or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def estimate_reading_time(word_count: int, words_per_minute: int = 200) -> int:
    """
    Estimate reading time in minutes.
    
    Args:
        word_count: Number of words
        words_per_minute: Average reading speed
        
    Returns:
        Estimated minutes
    """
    return max(1, word_count // words_per_minute)

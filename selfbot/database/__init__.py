"""
Database module for SelfEarnBot.
"""
from .models import (
    SelfBotDatabase,
    Opportunity,
    GeneratedContent,
    PublishResult,
    LearningRecord
)

__all__ = [
    'SelfBotDatabase',
    'Opportunity',
    'GeneratedContent',
    'PublishResult',
    'LearningRecord'
]

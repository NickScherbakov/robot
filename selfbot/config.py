"""
Configuration for SelfEarnBot module.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class SelfBotConfig:
    """SelfBot-specific configuration"""
    
    # Scanner settings
    SCAN_INTERVAL = int(os.getenv('SELFBOT_SCAN_INTERVAL', '300'))  # 5 minutes
    RSS_FEEDS = os.getenv('SELFBOT_RSS_FEEDS', '').split(',') if os.getenv('SELFBOT_RSS_FEEDS') else []
    
    # Finance settings
    INITIAL_BUDGET = float(os.getenv('SELFBOT_INITIAL_BUDGET', '10.00'))
    MIN_PROFIT_MARGIN = float(os.getenv('SELFBOT_MIN_PROFIT_MARGIN', '0.5'))  # 50%
    AUTO_REINVEST = os.getenv('SELFBOT_AUTO_REINVEST', 'true').lower() == 'true'
    REINVEST_PERCENTAGE = float(os.getenv('SELFBOT_REINVEST_PERCENTAGE', '50'))
    
    # Content generation
    DEFAULT_AI_PROVIDER = os.getenv('SELFBOT_DEFAULT_AI_PROVIDER', 'mistral')  # Use cheaper provider
    MAX_CONTENT_LENGTH = int(os.getenv('SELFBOT_MAX_CONTENT_LENGTH', '2000'))
    
    # Opportunity scoring
    MIN_OPPORTUNITY_SCORE = float(os.getenv('SELFBOT_MIN_OPPORTUNITY_SCORE', '0.7'))
    MAX_OPPORTUNITIES_PER_CYCLE = int(os.getenv('SELFBOT_MAX_OPPORTUNITIES_PER_CYCLE', '5'))
    
    # Publishing
    AUTO_PUBLISH = os.getenv('SELFBOT_AUTO_PUBLISH', 'false').lower() == 'true'
    REQUIRE_APPROVAL = os.getenv('SELFBOT_REQUIRE_APPROVAL', 'true').lower() == 'true'
    
    # Database
    DATABASE_PATH = os.getenv('SELFBOT_DATABASE_PATH', 'data/selfbot.db')
    
    # Learning
    ENABLE_LEARNING = os.getenv('SELFBOT_ENABLE_LEARNING', 'true').lower() == 'true'
    LEARNING_RATE = float(os.getenv('SELFBOT_LEARNING_RATE', '0.1'))
    
    # Economics (expected ranges in USD)
    ECONOMICS = {
        'content_article': {
            'revenue_min': 5.00,
            'revenue_max': 50.00,
            'ai_cost_min': 0.01,
            'ai_cost_max': 0.10,
            'margin': 0.95
        },
        'code_snippet': {
            'revenue_min': 10.00,
            'revenue_max': 100.00,
            'ai_cost_min': 0.02,
            'ai_cost_max': 0.20,
            'margin': 0.95
        },
        'seo_content': {
            'revenue_min': 3.00,
            'revenue_max': 30.00,
            'ai_cost_min': 0.01,
            'ai_cost_max': 0.08,
            'margin': 0.95
        }
    }
    
    @classmethod
    def validate(cls):
        """Validate SelfBot configuration"""
        if cls.INITIAL_BUDGET < 0:
            raise ValueError("Initial budget must be non-negative")
        if cls.MIN_PROFIT_MARGIN < 0 or cls.MIN_PROFIT_MARGIN > 1:
            raise ValueError("Minimum profit margin must be between 0 and 1")
        if cls.REINVEST_PERCENTAGE < 0 or cls.REINVEST_PERCENTAGE > 100:
            raise ValueError("Reinvest percentage must be between 0 and 100")
        return True

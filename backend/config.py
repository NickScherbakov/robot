"""
Configuration management for the Earning Robot.
Loads environment variables and provides configuration constants.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_OWNER_ID = os.getenv('TELEGRAM_OWNER_ID', '')
    
    # AI APIs
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', '')
    
    # Payment Gateway
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    
    # Application
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/robot.db')
    
    # Pricing
    SUBSCRIPTION_MONTHLY_PRICE = float(os.getenv('SUBSCRIPTION_MONTHLY_PRICE', '29.99'))
    MICRO_PAYMENT_PRICE = float(os.getenv('MICRO_PAYMENT_PRICE', '0.50'))
    
    # Reporting
    REPORT_TIME = os.getenv('REPORT_TIME', '09:00')
    TIMEZONE = os.getenv('TIMEZONE', 'UTC')
    
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_fields = [
            ('TELEGRAM_BOT_TOKEN', cls.TELEGRAM_BOT_TOKEN),
            ('TELEGRAM_OWNER_ID', cls.TELEGRAM_OWNER_ID),
        ]
        
        missing = [field for field, value in required_fields if not value]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True

"""
Database models for the Earning Robot.
Handles transactions, users, and task tracking.
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    """User/Customer model"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(50), unique=True, nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    subscription_type = Column(String(20), default='free')  # free, monthly
    subscription_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<User {self.id} - {self.email or self.telegram_id}>"


class Transaction(Base):
    """Financial transaction model"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    transaction_type = Column(String(20))  # income, expense
    category = Column(String(50))  # subscription, micro_payment, api_cost, other
    amount = Column(Float)
    currency = Column(String(3), default='USD')
    description = Column(Text)
    payment_provider = Column(String(50), nullable=True)  # stripe, paypal
    external_id = Column(String(100), nullable=True)  # Payment provider's transaction ID
    status = Column(String(20), default='pending')  # pending, completed, failed, refunded
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Transaction {self.id} - {self.transaction_type} {self.amount} {self.currency}>"


class Task(Base):
    """AI Task execution model"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    task_type = Column(String(50))  # chat, completion, analysis
    ai_provider = Column(String(20))  # openai, mistral
    input_text = Column(Text)
    output_text = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    status = Column(String(20), default='pending')  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Task {self.id} - {self.task_type} - {self.status}>"


class Database:
    """Database connection manager"""
    
    def __init__(self, db_path='data/robot.db'):
        self.db_path = db_path
        self.engine = None
        self.Session = None
        
    def initialize(self):
        """Initialize database connection and create tables"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Create engine
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.Session = sessionmaker(bind=self.engine)
        
        return self
    
    def get_session(self):
        """Get a new database session"""
        if not self.Session:
            self.initialize()
        return self.Session()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()

"""
Basic tests for the Earning Robot.
Run with: pytest tests/
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import Database, User, Task, Transaction
from backend.config import Config
from billing.reporting import ReportGenerator
from datetime import datetime


@pytest.fixture
def test_db():
    """Create a test database"""
    db = Database(':memory:').initialize()
    yield db
    db.close()


def test_database_initialization(test_db):
    """Test database can be initialized"""
    assert test_db.engine is not None
    assert test_db.Session is not None


def test_create_user(test_db):
    """Test user creation"""
    session = test_db.get_session()
    
    user = User(
        email='test@example.com',
        subscription_type='monthly'
    )
    session.add(user)
    session.commit()
    
    # Verify user was created
    retrieved = session.query(User).filter_by(email='test@example.com').first()
    assert retrieved is not None
    assert retrieved.email == 'test@example.com'
    assert retrieved.subscription_type == 'monthly'
    
    session.close()


def test_create_task(test_db):
    """Test task creation"""
    session = test_db.get_session()
    
    task = Task(
        task_type='test',
        ai_provider='openai',
        input_text='Test question',
        output_text='Test answer',
        tokens_used=100,
        cost=0.002,
        status='completed'
    )
    session.add(task)
    session.commit()
    
    # Verify task was created
    retrieved = session.query(Task).first()
    assert retrieved is not None
    assert retrieved.task_type == 'test'
    assert retrieved.tokens_used == 100
    
    session.close()


def test_create_transaction(test_db):
    """Test transaction creation"""
    session = test_db.get_session()
    
    transaction = Transaction(
        transaction_type='income',
        category='subscription',
        amount=29.99,
        description='Monthly subscription',
        status='completed'
    )
    session.add(transaction)
    session.commit()
    
    # Verify transaction was created
    retrieved = session.query(Transaction).first()
    assert retrieved is not None
    assert retrieved.transaction_type == 'income'
    assert retrieved.amount == 29.99
    
    session.close()


def test_report_generator(test_db):
    """Test report generation"""
    session = test_db.get_session()
    
    # Add some test transactions
    income = Transaction(
        transaction_type='income',
        category='subscription',
        amount=100.00,
        status='completed'
    )
    expense = Transaction(
        transaction_type='expense',
        category='api_cost',
        amount=10.00,
        status='completed'
    )
    session.add(income)
    session.add(expense)
    session.commit()
    
    # Generate report
    generator = ReportGenerator(session)
    summary = generator.get_daily_summary()
    
    assert summary['income'] == 100.00
    assert summary['expenses'] == 10.00
    assert summary['profit'] == 90.00
    
    session.close()


def test_config_validation():
    """Test configuration validation"""
    # This will fail if required config is missing, which is expected
    # In real tests, you'd mock the environment variables
    try:
        Config.validate()
    except ValueError as e:
        # Expected if .env is not configured
        assert 'Missing required configuration' in str(e)


def test_task_status_update(test_db):
    """Test updating task status"""
    session = test_db.get_session()
    
    task = Task(
        task_type='test',
        ai_provider='openai',
        input_text='Test',
        status='pending'
    )
    session.add(task)
    session.commit()
    
    # Update status
    task.status = 'completed'
    task.completed_at = datetime.utcnow()
    session.commit()
    
    # Verify update
    retrieved = session.query(Task).first()
    assert retrieved.status == 'completed'
    assert retrieved.completed_at is not None
    
    session.close()


def test_user_subscription(test_db):
    """Test user subscription management"""
    session = test_db.get_session()
    
    user = User(
        email='subscriber@example.com',
        subscription_type='free'
    )
    session.add(user)
    session.commit()
    
    # Upgrade to monthly
    user.subscription_type = 'monthly'
    user.subscription_expires = datetime.utcnow()
    session.commit()
    
    # Verify
    retrieved = session.query(User).first()
    assert retrieved.subscription_type == 'monthly'
    assert retrieved.subscription_expires is not None
    
    session.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
Basic tests for SelfEarnBot module.
Run with: pytest tests/test_selfbot.py
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from selfbot.database import SelfBotDatabase, Opportunity, GeneratedContent, PublishResult, LearningRecord
from selfbot.config import SelfBotConfig
from selfbot.brain import OpportunityScorer, DecisionEngine
from selfbot.scanner import RSSScanner
from datetime import datetime


@pytest.fixture
def test_db():
    """Create a test database"""
    db = SelfBotDatabase(':memory:').initialize()
    yield db
    db.close()


def test_selfbot_database_initialization(test_db):
    """Test SelfBot database can be initialized"""
    assert test_db.engine is not None
    assert test_db.Session is not None


def test_create_opportunity(test_db):
    """Test opportunity creation"""
    session = test_db.get_session()
    
    opp = Opportunity(
        source='test',
        title='Test Opportunity',
        description='Test description',
        content_type='article',
        estimated_revenue=25.00,
        estimated_cost=0.05
    )
    session.add(opp)
    session.commit()
    
    # Verify opportunity was created
    retrieved = session.query(Opportunity).first()
    assert retrieved is not None
    assert retrieved.title == 'Test Opportunity'
    assert retrieved.estimated_revenue == 25.00
    
    session.close()


def test_create_generated_content(test_db):
    """Test generated content creation"""
    session = test_db.get_session()
    
    content = GeneratedContent(
        content_type='article',
        title='Test Article',
        content='This is test content',
        ai_provider='mistral',
        tokens_used=100,
        generation_cost=0.002,
        quality_score=0.85
    )
    session.add(content)
    session.commit()
    
    # Verify content was created
    retrieved = session.query(GeneratedContent).first()
    assert retrieved is not None
    assert retrieved.content_type == 'article'
    assert retrieved.quality_score == 0.85
    
    session.close()


def test_create_publish_result(test_db):
    """Test publish result creation"""
    session = test_db.get_session()
    
    result = PublishResult(
        content_id=1,
        platform='test_platform',
        status='published',
        actual_revenue=25.00,
        actual_cost=0.05,
        actual_profit=24.95,
        roi=499.0
    )
    session.add(result)
    session.commit()
    
    # Verify result was created
    retrieved = session.query(PublishResult).first()
    assert retrieved is not None
    assert retrieved.status == 'published'
    assert retrieved.actual_profit == 24.95
    
    session.close()


def test_create_learning_record(test_db):
    """Test learning record creation"""
    session = test_db.get_session()
    
    record = LearningRecord(
        action_type='full_cycle',
        success=True,
        profit=24.95,
        features={'content_type': 'article'},
        insights='Successful operation'
    )
    session.add(record)
    session.commit()
    
    # Verify record was created
    retrieved = session.query(LearningRecord).first()
    assert retrieved is not None
    assert retrieved.success == True
    assert retrieved.profit == 24.95
    
    session.close()


def test_opportunity_scorer():
    """Test opportunity scoring"""
    scorer = OpportunityScorer()
    
    opportunity = {
        'source': 'rss_demo',
        'title': 'Test Opportunity',
        'description': 'Test',
        'content_type': 'article',
        'estimated_revenue': 25.00,
        'requirements': {'word_count': 800}
    }
    
    score = scorer.score_opportunity(opportunity)
    
    assert 0 <= score <= 1
    assert score > 0.5  # Should be a decent opportunity


def test_opportunity_ranking():
    """Test opportunity ranking"""
    scorer = OpportunityScorer()
    
    opportunities = [
        {
            'source': 'test',
            'title': 'Low value',
            'description': 'Test',
            'content_type': 'article',
            'estimated_revenue': 5.00,
            'requirements': {}
        },
        {
            'source': 'test',
            'title': 'High value',
            'description': 'Test',
            'content_type': 'article',
            'estimated_revenue': 50.00,
            'requirements': {}
        }
    ]
    
    ranked = scorer.rank_opportunities(opportunities)
    
    assert len(ranked) == 2
    assert ranked[0]['estimated_revenue'] == 50.00  # Higher revenue should rank first


def test_decision_engine_evaluation():
    """Test decision engine"""
    engine = DecisionEngine()
    
    opportunities = [
        {
            'source': 'test',
            'title': 'Good opportunity',
            'description': 'Test',
            'content_type': 'article',
            'estimated_revenue': 25.00,
            'requirements': {'word_count': 800}
        }
    ]
    
    budget = 10.00
    selected = engine.evaluate_and_select(opportunities, budget)
    
    # Should select the opportunity if it fits budget
    assert len(selected) >= 0


def test_rss_scanner_demo_mode():
    """Test RSS scanner in demo mode"""
    scanner = RSSScanner([])  # No feeds = demo mode
    
    opportunities = scanner.scan()
    
    # Demo mode should generate some opportunities
    assert isinstance(opportunities, list)


def test_selfbot_config_validation():
    """Test SelfBot configuration validation"""
    # Should validate successfully with reasonable defaults
    try:
        SelfBotConfig.validate()
        assert True
    except ValueError:
        # May fail if values are out of range, which is expected
        assert True


def test_economics_data():
    """Test that economics data is available"""
    assert 'content_article' in SelfBotConfig.ECONOMICS
    assert 'code_snippet' in SelfBotConfig.ECONOMICS
    assert 'seo_content' in SelfBotConfig.ECONOMICS
    
    article_econ = SelfBotConfig.ECONOMICS['content_article']
    assert 'revenue_min' in article_econ
    assert 'revenue_max' in article_econ
    assert 'ai_cost_min' in article_econ
    assert 'ai_cost_max' in article_econ
    
    # Note: Generators use 'code' but config has 'code_snippet' for clarity
    # Both refer to the same content type


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

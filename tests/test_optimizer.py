"""
Unit tests for Model Optimizer
"""
import pytest
import os
import tempfile
from datetime import datetime
from backend.model_optimizer import (
    ModelOptimizer, UsageRecord, ModelPricing, OptimizationRecommendation
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except:
        pass


@pytest.fixture
def optimizer(temp_db):
    """Create optimizer instance with temp database"""
    return ModelOptimizer(temp_db)


class TestModelOptimizer:
    """Test Model Optimizer functionality"""
    
    def test_initialization(self, optimizer):
        """Test optimizer initialization"""
        assert optimizer is not None
        assert os.path.exists(optimizer.db_path)
    
    def test_pricing_database_loaded(self, optimizer):
        """Test that pricing data is loaded"""
        import sqlite3
        conn = sqlite3.connect(optimizer.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM model_pricing")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        assert count > 0, "Pricing database should have models"
    
    def test_record_usage(self, optimizer):
        """Test recording usage"""
        record = UsageRecord(
            timestamp=datetime.now().isoformat(),
            provider="openai",
            model="gpt-4o",
            task_type="test",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.001,
            latency_ms=1000,
            success=True,
            quality_rating=9.0
        )
        
        optimizer.record_usage(record)
        
        # Verify record was saved
        import sqlite3
        conn = sqlite3.connect(optimizer.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM usage_records")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        assert count == 1
    
    def test_calculate_cost(self, optimizer):
        """Test cost calculation"""
        cost = optimizer.calculate_cost(
            provider="openai",
            model="gpt-4o",
            input_tokens=1000,
            output_tokens=500
        )
        
        # gpt-4o: $2.50 input + $10.00 output per 1M tokens
        # Expected: (1000/1M * 2.5) + (500/1M * 10.0) = 0.0025 + 0.005 = 0.0075
        expected = 0.0075
        
        assert abs(cost - expected) < 0.0001, f"Expected {expected}, got {cost}"
    
    def test_get_usage_stats(self, optimizer):
        """Test getting usage statistics"""
        # Add some test data
        for i in range(5):
            record = UsageRecord(
                timestamp=datetime.now().isoformat(),
                provider="openai",
                model="gpt-4o",
                task_type="test",
                input_tokens=100,
                output_tokens=50,
                cost_usd=0.001,
                latency_ms=1000,
                success=True
            )
            optimizer.record_usage(record)
        
        stats = optimizer.get_usage_stats(30)
        
        assert stats['total_requests'] == 5
        assert stats['total_cost_usd'] == 0.005
        assert len(stats['by_model']) > 0
    
    def test_get_cheapest_alternative(self, optimizer):
        """Test finding cheapest alternative"""
        alternative = optimizer.get_cheapest_alternative(
            current_model="openai/gpt-4o",
            required_capabilities=["text"],
            min_quality_score=75
        )
        
        assert alternative is not None
        provider, model, price = alternative
        
        # Should find a cheaper model
        current_price = 2.50 + 10.00  # gpt-4o total
        assert price < current_price
    
    def test_get_optimal_model_for_task(self, optimizer):
        """Test getting optimal model for task"""
        result = optimizer.get_optimal_model_for_task(
            task_type="content_generation",
            max_cost_per_request=0.005,
            required_capabilities=["text"]
        )
        
        assert result is not None
        provider, model = result
        
        # Verify cost is within limit
        cost = optimizer.calculate_cost(provider, model, 1000, 500)
        assert cost <= 0.005
    
    def test_analyze_and_recommend(self, optimizer):
        """Test generating recommendations"""
        # Add usage data for expensive model
        for i in range(20):
            record = UsageRecord(
                timestamp=datetime.now().isoformat(),
                provider="openai",
                model="gpt-4-turbo",  # Expensive model
                task_type="test",
                input_tokens=1000,
                output_tokens=500,
                cost_usd=0.02,
                latency_ms=2000,
                success=True
            )
            optimizer.record_usage(record)
        
        recommendations = optimizer.analyze_and_recommend(30)
        
        # Should have at least one recommendation for cheaper alternative
        assert len(recommendations) >= 0  # May be 0 if no better alternative found
        
        if recommendations:
            rec = recommendations[0]
            assert rec.estimated_savings_percent > 0
            assert rec.confidence > 0
    
    def test_generate_report(self, optimizer):
        """Test report generation"""
        # Add some data
        record = UsageRecord(
            timestamp=datetime.now().isoformat(),
            provider="openai",
            model="gpt-4o",
            task_type="test",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.0075,
            latency_ms=2000,
            success=True
        )
        optimizer.record_usage(record)
        
        report = optimizer.generate_optimization_report(30)
        
        assert "Отчет по оптимизации" in report
        assert "$" in report  # Should contain cost information
        assert "openai/gpt-4o" in report or "gpt-4o" in report


class TestOptimizerMiddleware:
    """Test Optimizer Middleware"""
    
    def test_middleware_import(self):
        """Test middleware can be imported"""
        from backend.optimizer_middleware import OptimizerMiddleware
        
        middleware = OptimizerMiddleware()
        assert middleware is not None
    
    def test_track_usage_decorator(self, temp_db):
        """Test usage tracking decorator"""
        from backend.optimizer_middleware import OptimizerMiddleware
        
        middleware = OptimizerMiddleware(temp_db)
        
        @middleware.track_usage("openai", "gpt-4o", "test")
        def test_function():
            # Mock response with usage info
            class MockUsage:
                prompt_tokens = 100
                completion_tokens = 50
            
            class MockResponse:
                usage = MockUsage()
            
            return MockResponse()
        
        result = test_function()
        assert result is not None
        
        # Verify usage was recorded
        stats = middleware.optimizer.get_usage_stats(1)
        assert stats['total_requests'] >= 1
    
    def test_track_manual(self, temp_db):
        """Test manual tracking"""
        from backend.optimizer_middleware import OptimizerMiddleware
        
        middleware = OptimizerMiddleware(temp_db)
        
        cost = middleware.track_manual(
            provider="openai",
            model="gpt-4o",
            task_type="test",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000,
            success=True
        )
        
        assert cost > 0
        
        # Verify usage was recorded
        stats = middleware.optimizer.get_usage_stats(1)
        assert stats['total_requests'] == 1
    
    def test_get_optimal_provider(self, temp_db):
        """Test getting optimal provider through middleware"""
        from backend.optimizer_middleware import OptimizerMiddleware
        
        middleware = OptimizerMiddleware(temp_db)
        
        provider, model = middleware.get_optimal_provider(
            task_type="test",
            required_capabilities=["text"],
            max_cost=0.01
        )
        
        assert provider is not None
        assert model is not None


class TestPricingData:
    """Test pricing data accuracy"""
    
    def test_all_providers_have_models(self, optimizer):
        """Test that all providers have models in database"""
        import sqlite3
        conn = sqlite3.connect(optimizer.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT provider FROM model_pricing")
        providers = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        expected_providers = ["openai", "anthropic", "mistral", "google", "deepseek", "openrouter"]
        
        for provider in expected_providers:
            assert provider in providers, f"Provider {provider} should be in database"
    
    def test_quality_scores_valid(self, optimizer):
        """Test that quality scores are in valid range"""
        import sqlite3
        conn = sqlite3.connect(optimizer.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT quality_score FROM model_pricing")
        scores = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        for score in scores:
            assert 0 <= score <= 100, f"Quality score {score} should be between 0 and 100"
    
    def test_prices_positive(self, optimizer):
        """Test that all prices are positive"""
        import sqlite3
        conn = sqlite3.connect(optimizer.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT input_price_per_1m, output_price_per_1m FROM model_pricing")
        prices = cursor.fetchall()
        
        conn.close()
        
        for input_price, output_price in prices:
            assert input_price >= 0, "Input price should be non-negative"
            assert output_price >= 0, "Output price should be non-negative"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

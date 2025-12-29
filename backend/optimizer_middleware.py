"""
Middleware для автоматического логирования использования AI моделей.

Прозрачно интегрируется с существующими AI провайдерами
и автоматически записывает каждый запрос в Model Optimizer.
"""

import time
from functools import wraps
from typing import Callable, Any
from datetime import datetime
from backend.model_optimizer import ModelOptimizer, UsageRecord
import os


class OptimizerMiddleware:
    """Middleware для автоматического логирования использования моделей."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.getenv('OPTIMIZER_DB_PATH', 'data/optimizer.db')
        self.optimizer = ModelOptimizer(db_path)
        self.enabled = os.getenv('OPTIMIZER_ENABLED', 'true').lower() == 'true'
    
    def track_usage(self, provider: str, model: str, task_type: str = "general"):
        """
        Декоратор для отслеживания использования модели.
        
        Usage:
            @middleware.track_usage("openai", "gpt-4o", "content_generation")
            def generate_content(prompt):
                return openai_client.chat.completions.create(...)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                if not self.enabled:
                    return func(*args, **kwargs)
                
                start_time = time.time()
                success = False
                input_tokens = 0
                output_tokens = 0
                error = None
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    
                    # Извлекаем информацию о токенах из результата
                    if hasattr(result, 'usage'):
                        # OpenAI format
                        input_tokens = getattr(result.usage, 'prompt_tokens', 0)
                        output_tokens = getattr(result.usage, 'completion_tokens', 0)
                    elif isinstance(result, dict):
                        # Generic dict format
                        usage = result.get('usage', {})
                        input_tokens = usage.get('prompt_tokens', usage.get('input_tokens', 0))
                        output_tokens = usage.get('completion_tokens', usage.get('output_tokens', 0))
                    
                    return result
                
                except Exception as e:
                    error = e
                    raise
                
                finally:
                    latency_ms = int((time.time() - start_time) * 1000)
                    
                    # Рассчитываем стоимость
                    cost = self.optimizer.calculate_cost(
                        provider, model, input_tokens, output_tokens
                    )
                    
                    # Записываем использование
                    record = UsageRecord(
                        timestamp=datetime.now().isoformat(),
                        provider=provider,
                        model=model,
                        task_type=task_type,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        cost_usd=cost,
                        latency_ms=latency_ms,
                        success=success,
                        quality_rating=None
                    )
                    
                    try:
                        self.optimizer.record_usage(record)
                    except Exception as log_error:
                        # Не падаем если не удалось залогировать
                        print(f"Warning: Failed to log usage: {log_error}")
            
            return wrapper
        return decorator
    
    def track_manual(self, provider: str, model: str, task_type: str,
                    input_tokens: int, output_tokens: int,
                    latency_ms: int, success: bool = True,
                    quality_rating: float = None):
        """
        Ручная запись использования модели.
        
        Используется когда автоматический декоратор не подходит.
        """
        if not self.enabled:
            return
        
        cost = self.optimizer.calculate_cost(
            provider, model, input_tokens, output_tokens
        )
        
        record = UsageRecord(
            timestamp=datetime.now().isoformat(),
            provider=provider,
            model=model,
            task_type=task_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
            success=success,
            quality_rating=quality_rating
        )
        
        self.optimizer.record_usage(record)
        return cost
    
    def get_optimal_provider(self, task_type: str, 
                           required_capabilities: list = None,
                           max_cost: float = None) -> tuple:
        """
        Получить оптимального провайдера для задачи.
        
        Returns:
            (provider, model) или (None, None) если ничего не найдено
        """
        result = self.optimizer.get_optimal_model_for_task(
            task_type=task_type,
            max_cost_per_request=max_cost,
            required_capabilities=required_capabilities or ['text']
        )
        
        if result:
            return result
        return (None, None)


# Глобальный экземпляр middleware
_global_middleware = None


def get_optimizer_middleware() -> OptimizerMiddleware:
    """Получить глобальный экземпляр middleware."""
    global _global_middleware
    if _global_middleware is None:
        _global_middleware = OptimizerMiddleware()
    return _global_middleware


# Удобные функции для прямого использования
def track_usage(provider: str, model: str, task_type: str = "general"):
    """Декоратор для отслеживания использования."""
    return get_optimizer_middleware().track_usage(provider, model, task_type)


def track_manual(provider: str, model: str, task_type: str,
                input_tokens: int, output_tokens: int,
                latency_ms: int, success: bool = True,
                quality_rating: float = None):
    """Ручная запись использования."""
    return get_optimizer_middleware().track_manual(
        provider, model, task_type, input_tokens, output_tokens,
        latency_ms, success, quality_rating
    )


def get_optimal_provider(task_type: str, 
                        required_capabilities: list = None,
                        max_cost: float = None):
    """Получить оптимального провайдера."""
    return get_optimizer_middleware().get_optimal_provider(
        task_type, required_capabilities, max_cost
    )


# Пример использования
if __name__ == "__main__":
    middleware = OptimizerMiddleware()
    
    # Пример с декоратором
    @middleware.track_usage("openai", "gpt-4o", "test")
    def test_function():
        # Симуляция ответа от API
        class MockUsage:
            prompt_tokens = 100
            completion_tokens = 50
        
        class MockResponse:
            usage = MockUsage()
        
        time.sleep(0.1)  # Симуляция задержки
        return MockResponse()
    
    # Вызов функции - использование будет автоматически залогировано
    result = test_function()
    print("Test completed")
    
    # Пример с ручным логированием
    middleware.track_manual(
        provider="anthropic",
        model="claude-3-opus-20240229",
        task_type="content_generation",
        input_tokens=500,
        output_tokens=300,
        latency_ms=1500,
        success=True,
        quality_rating=9.5
    )
    print("Manual tracking completed")

"""
Примеры использования Model Optimizer.

Демонстрация основных сценариев работы с оптимизатором.
"""

from backend.model_optimizer import ModelOptimizer, UsageRecord
from backend.optimizer_middleware import OptimizerMiddleware
from datetime import datetime, timedelta
import random


def example_1_basic_usage():
    """Пример 1: Базовое использование"""
    print("\n" + "="*60)
    print("ПРИМЕР 1: Базовое использование Model Optimizer")
    print("="*60)
    
    optimizer = ModelOptimizer("data/optimizer_example.db")
    
    # Записываем использование модели
    print("\n1. Записываем использование GPT-4o...")
    record = UsageRecord(
        timestamp=datetime.now().isoformat(),
        provider="openai",
        model="gpt-4o",
        task_type="content_generation",
        input_tokens=1500,
        output_tokens=800,
        cost_usd=0.0115,
        latency_ms=2500,
        success=True,
        quality_rating=9.2
    )
    optimizer.record_usage(record)
    print("✅ Записано")
    
    # Получаем статистику
    print("\n2. Получаем статистику за 30 дней...")
    stats = optimizer.get_usage_stats(30)
    print(f"   Всего запросов: {stats['total_requests']}")
    print(f"   Общие затраты: ${stats['total_cost_usd']:.4f}")
    print(f"   Средняя стоимость: ${stats['average_cost_per_request']:.4f}")
    
    # Рассчитываем стоимость запроса
    print("\n3. Рассчитываем стоимость запроса...")
    cost = optimizer.calculate_cost("openai", "gpt-4o", 1000, 500)
    print(f"   Стоимость 1000 input + 500 output токенов: ${cost:.4f}")


def example_2_find_alternatives():
    """Пример 2: Поиск дешевых альтернатив"""
    print("\n" + "="*60)
    print("ПРИМЕР 2: Поиск дешевых альтернатив")
    print("="*60)
    
    optimizer = ModelOptimizer("data/optimizer_example.db")
    
    current_model = "openai/gpt-4o"
    print(f"\nТекущая модель: {current_model}")
    
    # Ищем более дешевую альтернативу
    alternative = optimizer.get_cheapest_alternative(
        current_model=current_model,
        required_capabilities=["text"],
        min_quality_score=80
    )
    
    if alternative:
        provider, model, price = alternative
        print(f"\n💡 Найдена альтернатива: {provider}/{model}")
        print(f"   Цена: ${price:.2f} за 1M токенов")
        
        # Сравниваем стоимость
        current_cost = optimizer.calculate_cost("openai", "gpt-4o", 10000, 5000)
        alt_cost = optimizer.calculate_cost(provider, model, 10000, 5000)
        
        savings = ((current_cost - alt_cost) / current_cost) * 100
        
        print(f"\n📊 Сравнение для 10k input + 5k output токенов:")
        print(f"   Текущая: ${current_cost:.4f}")
        print(f"   Альтернатива: ${alt_cost:.4f}")
        print(f"   Экономия: {savings:.1f}%")
    else:
        print("\n✅ Текущая модель уже оптимальна!")


def example_3_optimal_for_task():
    """Пример 3: Подбор оптимальной модели для задачи"""
    print("\n" + "="*60)
    print("ПРИМЕР 3: Подбор оптимальной модели для задачи")
    print("="*60)
    
    optimizer = ModelOptimizer("data/optimizer_example.db")
    
    # Задача: генерация кода с лимитом $0.01 за запрос
    print("\n📝 Задача: генерация кода")
    print("   Лимит: $0.01 за запрос")
    print("   Требования: text, code")
    
    result = optimizer.get_optimal_model_for_task(
        task_type="code_generation",
        max_cost_per_request=0.01,
        required_capabilities=["text", "code"]
    )
    
    if result:
        provider, model = result
        print(f"\n✅ Рекомендуется: {provider}/{model}")
        
        # Оцениваем стоимость
        cost = optimizer.calculate_cost(provider, model, 1000, 500)
        print(f"   Примерная стоимость: ${cost:.4f} за запрос")
    else:
        print("\n❌ Не найдено подходящих моделей")


def example_4_recommendations():
    """Пример 4: Генерация рекомендаций"""
    print("\n" + "="*60)
    print("ПРИМЕР 4: Генерация рекомендаций по оптимизации")
    print("="*60)
    
    optimizer = ModelOptimizer("data/optimizer_example.db")
    
    # Добавляем немного тестовых данных
    print("\n1. Добавляем тестовые данные...")
    
    models = [
        ("openai", "gpt-4o", 0.0115),
        ("openai", "gpt-4-turbo", 0.025),
        ("anthropic", "claude-3-opus-20240229", 0.03),
    ]
    
    for provider, model, cost in models:
        for _ in range(15):
            record = UsageRecord(
                timestamp=datetime.now().isoformat(),
                provider=provider,
                model=model,
                task_type="content_generation",
                input_tokens=random.randint(800, 1200),
                output_tokens=random.randint(400, 600),
                cost_usd=cost + random.uniform(-0.002, 0.002),
                latency_ms=random.randint(1500, 3000),
                success=True,
                quality_rating=random.uniform(8.0, 9.5)
            )
            optimizer.record_usage(record)
    
    print("   ✅ Добавлено 45 записей")
    
    # Генерируем рекомендации
    print("\n2. Генерируем рекомендации...")
    recommendations = optimizer.analyze_and_recommend(30)
    
    if recommendations:
        print(f"\n💡 Найдено {len(recommendations)} рекомендаций:")
        
        total_savings = sum(r.estimated_savings_usd_monthly for r in recommendations)
        print(f"💰 Потенциальная экономия: ${total_savings:.2f}/месяц")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec.current_model} → {rec.recommended_model}")
            print(f"   Экономия: {rec.estimated_savings_percent:.1f}% (${rec.estimated_savings_usd_monthly:.2f}/мес)")
            print(f"   Влияние на качество: {rec.quality_impact}")
            print(f"   Уверенность: {rec.confidence:.0%}")
    else:
        print("\n✅ Нет рекомендаций - использование уже оптимально!")


def example_5_full_report():
    """Пример 5: Полный отчет"""
    print("\n" + "="*60)
    print("ПРИМЕР 5: Генерация полного отчета")
    print("="*60)
    
    optimizer = ModelOptimizer("data/optimizer_example.db")
    
    report = optimizer.generate_optimization_report(30)
    print(report)


def example_6_middleware():
    """Пример 6: Использование Middleware"""
    print("\n" + "="*60)
    print("ПРИМЕР 6: Автоматическое отслеживание через Middleware")
    print("="*60)
    
    middleware = OptimizerMiddleware("data/optimizer_example.db")
    
    # Пример 1: Декоратор
    print("\n1. Использование декоратора...")
    
    @middleware.track_usage("openai", "gpt-4o", "content_generation")
    def generate_content(prompt):
        """Симуляция вызова AI API"""
        import time
        
        class MockUsage:
            prompt_tokens = len(prompt.split()) * 2  # Примерная оценка
            completion_tokens = 100
        
        class MockResponse:
            usage = MockUsage()
            content = f"Ответ на: {prompt}"
        
        time.sleep(0.1)  # Симуляция задержки API
        return MockResponse()
    
    result = generate_content("Напиши статью про AI")
    print(f"   ✅ Запрос выполнен и залогирован автоматически")
    
    # Пример 2: Ручное логирование
    print("\n2. Ручное логирование...")
    
    cost = middleware.track_manual(
        provider="anthropic",
        model="claude-3-haiku-20240307",
        task_type="content_generation",
        input_tokens=500,
        output_tokens=300,
        latency_ms=1200,
        success=True,
        quality_rating=8.5
    )
    
    print(f"   ✅ Залогировано. Стоимость: ${cost:.4f}")
    
    # Пример 3: Получение оптимального провайдера
    print("\n3. Получение оптимального провайдера...")
    
    provider, model = middleware.get_optimal_provider(
        task_type="content_generation",
        required_capabilities=["text"],
        max_cost=0.01
    )
    
    print(f"   ✅ Рекомендуется: {provider}/{model}")


def example_7_cost_comparison():
    """Пример 7: Сравнение стоимости разных моделей"""
    print("\n" + "="*60)
    print("ПРИМЕР 7: Сравнение стоимости разных моделей")
    print("="*60)
    
    optimizer = ModelOptimizer("data/optimizer_example.db")
    
    # Типичный запрос: 1500 input, 800 output токенов
    input_tokens = 1500
    output_tokens = 800
    
    print(f"\nСравнение для {input_tokens} input + {output_tokens} output токенов:\n")
    
    models = [
        ("openai", "gpt-4o"),
        ("openai", "gpt-4o-mini"),
        ("openai", "gpt-3.5-turbo"),
        ("anthropic", "claude-3-opus-20240229"),
        ("anthropic", "claude-3-sonnet-20240229"),
        ("anthropic", "claude-3-haiku-20240307"),
        ("mistral", "mistral-large-latest"),
        ("mistral", "mistral-small-latest"),
        ("google", "gemini-1.5-pro"),
        ("google", "gemini-1.5-flash"),
    ]
    
    results = []
    
    for provider, model in models:
        cost = optimizer.calculate_cost(provider, model, input_tokens, output_tokens)
        if cost > 0:
            results.append((f"{provider}/{model}", cost))
    
    # Сортируем по цене
    results.sort(key=lambda x: x[1])
    
    print("Модель                                     | Стоимость  | Относительно")
    print("-" * 70)
    
    base_cost = results[0][1]
    
    for model_name, cost in results:
        relative = (cost / base_cost - 1) * 100
        relative_str = f"+{relative:.0f}%" if relative > 0 else "базовая"
        print(f"{model_name:42} | ${cost:8.4f} | {relative_str}")
    
    print("\n💡 Самая дешевая модель: " + results[0][0])
    print(f"💰 Можно сэкономить до {(results[-1][1] / results[0][1] - 1) * 100:.0f}% выбирая оптимальную модель")


def main():
    """Запуск всех примеров"""
    print("\n" + "="*60)
    print("🚀 MODEL OPTIMIZER - ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ")
    print("="*60)
    
    examples = [
        ("Базовое использование", example_1_basic_usage),
        ("Поиск дешевых альтернатив", example_2_find_alternatives),
        ("Подбор оптимальной модели", example_3_optimal_for_task),
        ("Генерация рекомендаций", example_4_recommendations),
        ("Полный отчет", example_5_full_report),
        ("Использование Middleware", example_6_middleware),
        ("Сравнение стоимости", example_7_cost_comparison),
    ]
    
    print("\nДоступные примеры:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. Запустить все примеры")
    
    choice = input("\nВыберите пример (0-7): ").strip()
    
    if choice == "0":
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\n❌ Ошибка в примере '{name}': {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        _, func = examples[int(choice) - 1]
        func()
    else:
        print("\n❌ Неверный выбор")
    
    print("\n" + "="*60)
    print("✅ Примеры завершены")
    print("="*60)


if __name__ == "__main__":
    main()

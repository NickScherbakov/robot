# 📊 Model Optimizer - Оптимизация затрат на AI модели

## Обзор

Model Optimizer - это инструмент для оптимизации затрат на использование AI моделей, аналогичный Google Cloud Vertex AI Model Optimizer. Система автоматически отслеживает использование, анализирует затраты и предлагает более экономичные альтернативы.

## Возможности

### 🎯 Основной функционал

- **Автоматическое отслеживание использования** - каждый запрос к AI моделям логируется
- **База данных цен** - актуальные цены на 15+ моделей от разных провайдеров
- **Анализ и рекомендации** - автоматический поиск более дешевых альтернатив
- **Детальная аналитика** - статистика по моделям, задачам, затратам
- **REST API** - полный доступ через HTTP API
- **CLI интерфейс** - команды для работы с оптимизатором

### 💰 Поддерживаемые провайдеры

1. **OpenAI** - GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
2. **Anthropic** - Claude 3 Opus, Sonnet, Haiku
3. **Mistral AI** - Large, Medium, Small
4. **Google** - Gemini 1.5 Pro, Flash
5. **DeepSeek** - Chat, Coder
6. **OpenRouter** - Агрегатор моделей

## Установка

Model Optimizer автоматически интегрирован в проект:

```bash
# Зависимости уже в requirements.txt
pip install -r requirements.txt

# База данных создается автоматически при первом запуске
python -m backend.model_optimizer
```

## Использование

### 1. Автоматическое отслеживание через Middleware

```python
from backend.optimizer_middleware import track_usage

@track_usage("openai", "gpt-4o", "content_generation")
def generate_content(prompt):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response
```

### 2. Ручное логирование

```python
from backend.optimizer_middleware import track_manual

track_manual(
    provider="anthropic",
    model="claude-3-opus-20240229",
    task_type="content_generation",
    input_tokens=500,
    output_tokens=300,
    latency_ms=1500,
    success=True,
    quality_rating=9.5
)
```

### 3. Получение оптимальной модели

```python
from backend.optimizer_middleware import get_optimal_provider

provider, model = get_optimal_provider(
    task_type="content_generation",
    required_capabilities=["text", "vision"],
    max_cost=0.01  # максимум $0.01 за запрос
)

print(f"Рекомендуется: {provider}/{model}")
```

### 4. Использование через API

#### Получить статистику

```bash
curl http://localhost:5000/api/optimizer/stats?days=30
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "period_days": 30,
    "total_cost_usd": 15.42,
    "total_requests": 1234,
    "average_cost_per_request": 0.0125,
    "by_model": [
      {
        "model": "openai/gpt-4o",
        "requests": 500,
        "cost_usd": 12.50,
        "avg_latency_ms": 2300,
        "avg_quality": 9.1
      }
    ]
  }
}
```

#### Получить рекомендации

```bash
curl http://localhost:5000/api/optimizer/recommendations?days=30
```

**Ответ:**
```json
{
  "success": true,
  "count": 2,
  "total_potential_savings_monthly": 45.60,
  "recommendations": [
    {
      "current_model": "openai/gpt-4o",
      "recommended_model": "anthropic/claude-3-haiku-20240307",
      "estimated_savings_percent": 75.0,
      "estimated_savings_usd_monthly": 37.50,
      "quality_impact": "minimal",
      "reason": "Модель anthropic/claude-3-haiku-20240307 дешевле на 75.0% при сопоставимом качестве",
      "confidence": 0.8
    }
  ]
}
```

#### Получить полный отчет

```bash
curl http://localhost:5000/api/optimizer/report?days=30&format=markdown
```

#### Найти оптимальную модель

```bash
curl -X POST http://localhost:5000/api/optimizer/optimal-model \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "content_generation",
    "max_cost_per_request": 0.01,
    "required_capabilities": ["text", "code"]
  }'
```

**Ответ:**
```json
{
  "success": true,
  "provider": "mistral",
  "model": "mistral-small-latest",
  "estimated_cost_per_request": 0.008,
  "full_model_name": "mistral/mistral-small-latest"
}
```

#### Рассчитать стоимость запроса

```bash
curl -X POST http://localhost:5000/api/optimizer/cost-calculator \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "model": "gpt-4o",
    "input_tokens": 1500,
    "output_tokens": 800
  }'
```

**Ответ:**
```json
{
  "success": true,
  "provider": "openai",
  "model": "gpt-4o",
  "input_tokens": 1500,
  "output_tokens": 800,
  "cost_usd": 0.01175,
  "cost_per_1k_tokens": 0.00511
}
```

#### Получить цены на все модели

```bash
curl http://localhost:5000/api/optimizer/pricing?min_quality=80&max_price=10
```

### 5. Использование через CLI

```bash
# Запуск CLI
python cli.py

# В меню выберите:
# 7 - Статистика Model Optimizer
# 8 - Рекомендации по оптимизации
# 9 - Полный отчет
```

**Пример вывода рекомендаций:**

```
💡 Found 2 optimization opportunities
💰 Total Potential Savings: $45.60/month

1. openai/gpt-4o → anthropic/claude-3-haiku-20240307
   Savings: 75.0% ($37.50/mo)
   Quality Impact: minimal
   Reason: Модель anthropic/claude-3-haiku-20240307 дешевле на 75.0% при сопоставимом качестве
   Confidence: 80%

2. anthropic/claude-3-opus-20240229 → openai/gpt-4o-mini
   Savings: 92.0% ($8.10/mo)
   Quality Impact: moderate
   Reason: Модель openai/gpt-4o-mini дешевле на 92.0% при сопоставимом качестве
   Confidence: 60%
```

## Архитектура

### Компоненты системы

```
backend/
├── model_optimizer.py        # Основной класс оптимизатора
├── optimizer_api.py          # REST API endpoints
└── optimizer_middleware.py   # Middleware для автоматического логирования
```

### База данных

**Таблицы:**

1. **model_pricing** - цены на модели
   - provider, model, input_price_per_1m, output_price_per_1m
   - context_window, capabilities, quality_score, speed_score

2. **usage_records** - записи использования
   - timestamp, provider, model, task_type
   - input_tokens, output_tokens, cost_usd
   - latency_ms, success, quality_rating

3. **recommendations** - история рекомендаций
   - current_model, recommended_model
   - estimated_savings_percent, quality_impact
   - applied (применена ли рекомендация)

### Алгоритм оптимизации

1. **Сбор данных** - автоматическое логирование каждого запроса
2. **Анализ паттернов** - выявление часто используемых моделей
3. **Поиск альтернатив** - сравнение с другими моделями по:
   - Цене (основной фактор)
   - Качеству (допускается снижение до 10 баллов)
   - Возможностям (должны совпадать)
4. **Оценка экономии** - расчет потенциальной экономии
5. **Ранжирование** - сортировка по уверенности и экономии

## Конфигурация

### Переменные окружения

```bash
# .env
OPTIMIZER_DB_PATH=data/optimizer.db
OPTIMIZER_ENABLED=true
```

### Настройка качества

При поиске альтернатив можно настроить минимальный уровень качества:

```python
optimizer = ModelOptimizer()

# Искать альтернативы с качеством не ниже 75
alternative = optimizer.get_cheapest_alternative(
    current_model="openai/gpt-4o",
    required_capabilities=["text"],
    min_quality_score=75
)
```

## Метрики качества

### Quality Score (0-100)

Оценка общего качества модели на основе:
- Точность ответов
- Следование инструкциям
- Креативность
- Консистентность

**Примеры:**
- GPT-4o: 95
- Claude 3 Opus: 98
- GPT-4o-mini: 85
- Gemini Flash: 82

### Speed Score (0-100)

Оценка скорости работы модели:
- Latency (время ответа)
- Throughput (токенов в секунду)

**Примеры:**
- GPT-3.5-turbo: 98 (очень быстрая)
- Gemini Flash: 98
- GPT-4o: 85 (средняя)
- Claude 3 Opus: 65 (медленная)

## Примеры использования

### Пример 1: Минимизация затрат на контент

```python
from backend.model_optimizer import ModelOptimizer

optimizer = ModelOptimizer()

# Текущая модель: gpt-4o ($2.50 input + $10.00 output)
# Задача: генерация текстового контента

# Находим более дешевую альтернативу
provider, model = optimizer.get_optimal_model_for_task(
    task_type="content_generation",
    max_cost_per_request=0.005,  # Лимит $0.005
    required_capabilities=["text"]
)

# Результат: mistral/mistral-small-latest
# Экономия: 80%
```

### Пример 2: Анализ затрат за месяц

```python
stats = optimizer.get_usage_stats(30)

print(f"Затраты за месяц: ${stats['total_cost_usd']:.2f}")
print(f"Всего запросов: {stats['total_requests']}")

# Топ-3 самых дорогих моделей
for model in stats['by_model'][:3]:
    print(f"{model['model']}: ${model['cost_usd']:.2f}")
```

### Пример 3: Автоматический отчет

```python
report = optimizer.generate_optimization_report(30)

# Отправить отчет владельцу
send_email(
    to="owner@example.com",
    subject="Monthly AI Optimization Report",
    body=report
)
```

## Интеграция с планировщиком

Автоматическая генерация отчетов можно настроить через scheduler:

```python
# backend/scheduler.py

from backend.model_optimizer import ModelOptimizer
from frontend.telegram_bot import send_message_to_owner

def generate_weekly_optimizer_report():
    """Еженедельный отчет по оптимизации"""
    optimizer = ModelOptimizer()
    report = optimizer.generate_optimization_report(7)
    send_message_to_owner(f"📊 Weekly Optimization Report:\n\n{report}")

# Добавить в расписание
schedule.every().monday.at("09:00").do(generate_weekly_optimizer_report)
```

## FAQ

### Как часто обновляются цены?

Цены обновляются вручную при изменении тарифов провайдерами. Рекомендуется проверять актуальность раз в месяц.

### Можно ли добавить свою модель?

Да, через API или напрямую в базу:

```python
from backend.model_optimizer import ModelOptimizer, ModelPricing
from datetime import datetime

optimizer = ModelOptimizer()

new_model = ModelPricing(
    provider="custom",
    model="my-model",
    input_price_per_1m=1.0,
    output_price_per_1m=2.0,
    context_window=8192,
    capabilities=["text"],
    quality_score=85,
    speed_score=90,
    last_updated=datetime.now().isoformat()
)

# Сохранение в БД реализуется через SQL INSERT
```

### Как оптимизатор влияет на производительность?

Минимальное влияние:
- Логирование асинхронное
- База данных SQLite (быстрая)
- Анализ происходит по запросу, а не в реальном времени

### Можно ли отключить оптимизатор?

Да, через переменную окружения:

```bash
export OPTIMIZER_ENABLED=false
```

## Roadmap

- [ ] Автоматическое обновление цен через API провайдеров
- [ ] ML-модель для предсказания оптимальной модели
- [ ] A/B тестирование моделей
- [ ] Интеграция с Grafana для визуализации
- [ ] Автоматическое переключение моделей на основе рекомендаций
- [ ] Поддержка кастомных метрик качества

## Поддержка

При возникновении проблем:
1. Проверьте логи: `data/optimizer.db`
2. Убедитесь что OPTIMIZER_ENABLED=true
3. Проверьте права доступа к файлу БД

---

**Создан:** 2025-12-29  
**Версия:** 1.0.0  
**Лицензия:** MIT

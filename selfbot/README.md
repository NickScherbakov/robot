# 🤖 SelfEarnBot - AI Content Arbitrage Bot

## 🎯 Concept

**SelfEarnBot** is an autonomous bot that **makes money on its own** without human intervention, using TRIZ principles (Theory of Inventive Problem Solving) and content arbitrage.

### ICR (Ideal Final Result)

> The bot **INDEPENDENTLY** finds opportunities, **INDEPENDENTLY** makes decisions, **INDEPENDENTLY** earns, **INDEPENDENTLY** reinvests.

## 🏗️ Архитектура

### Основные модули

```
selfbot/
├── scanner/          # Поиск возможностей
│   ├── rss_monitor.py      - RSS-фиды
│   ├── freelance.py        - Фриланс-платформы (демо)
│   └── content_markets.py  - Контент-биржи
│
├── generator/        # Генерация контента
│   ├── articles.py   - Статьи и блог-посты
│   ├── code.py       - Код и скрипты
│   └── images.py     - Изображения (заглушка)
│
├── publisher/        # Публикация
│   ├── freelance.py  - Фриланс-платформы
│   └── platforms.py  - Medium, Dev.to, и др.
│
├── brain/            # Принятие решений
│   ├── decision_engine.py   - Главный движок решений
│   ├── opportunity_scorer.py - Оценка возможностей
│   └── strategy.py          - Стратегии заработка
│
├── finance/          # Финансы
│   ├── tracker.py    - Трекинг доходов/расходов
│   ├── reinvestor.py - Автореинвестирование
│   └── reports.py    - Отчёты
│
├── evolution/        # Обучение
│   ├── learner.py    - Обучение на опыте
│   └── optimizer.py  - Оптимизация стратегий
│
├── database/         # База данных
│   └── models.py     - Модели данных
│
└── main.py          # Главный цикл бота
```

## 🔄 Цикл работы бота

```python
while True:
    # 1. Сканируем возможности
    opportunities = scanner.find_opportunities()
    
    # 2. Мозг оценивает и выбирает лучшие
    best = brain.evaluate_and_select(opportunities, budget)
    
    # 3. Генерируем контент через AI
    content = generator.create(best.requirements)
    
    # 4. Публикуем/отправляем
    result = publisher.submit(content, best.target)
    
    # 5. Трекаем финансы
    finance.record_transaction(result)
    
    # 6. Обучаемся на результате
    evolution.learn(result)
    
    # 7. Реинвестируем прибыль
    if result.profitable:
        finance.reinvest(profit * reinvest_percentage)
```

## 💰 Юнит-экономика

```python
ECONOMICS = {
    "content_article": {
        "revenue": "$5 - $50",      # Доход за статью
        "ai_cost": "$0.01 - $0.10", # Стоимость генерации
        "margin": "~95%"            # Маржа
    },
    "code_snippet": {
        "revenue": "$10 - $100",
        "ai_cost": "$0.02 - $0.20",
        "margin": "~95%"
    },
    "seo_content": {
        "revenue": "$3 - $30",
        "ai_cost": "$0.01 - $0.08",
        "margin": "~95%"
    }
}
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Уже установлены в основном проекте
pip install -r requirements.txt
```

### 2. Конфигурация

Добавьте в `.env`:

```env
# SelfBot Configuration
SELFBOT_SCAN_INTERVAL=300           # Интервал сканирования (сек)
SELFBOT_INITIAL_BUDGET=10.00        # Начальный бюджет ($)
SELFBOT_MIN_PROFIT_MARGIN=0.5       # Минимальная маржа (50%)
SELFBOT_AUTO_REINVEST=true          # Авто-реинвестирование
SELFBOT_REINVEST_PERCENTAGE=50      # % реинвестирования
SELFBOT_DEFAULT_AI_PROVIDER=mistral # AI провайдер по умолчанию
SELFBOT_AUTO_PUBLISH=false          # Авто-публикация
SELFBOT_REQUIRE_APPROVAL=true       # Требовать одобрения
SELFBOT_ENABLE_LEARNING=true        # Включить обучение

# AI API Keys (используются из основной конфигурации)
OPENAI_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here
```

### 3. Запуск

```bash
# Запуск SelfBot
python selfbot/main.py

# Или через модуль
python -m selfbot.main
```

## 📊 Как это работает

### Шаг 1: Сканирование возможностей

Бот сканирует:
- **RSS-фиды** - запросы на контент
- **Фриланс-платформы** - заказы (демо-режим)
- **Контент-биржи** - трендовые темы

```
📡 Scanning for opportunities...
  RSSScanner: found 2 opportunities
  FreelanceScanner: found 1 opportunities
  ContentMarketScanner: found 1 opportunities
```

### Шаг 2: Оценка и выбор

"Мозг" оценивает каждую возможность по:
- Прибыльности (profit margin)
- Потенциальному доходу
- Сложности выполнения
- Надёжности источника

```
🧠 Evaluating opportunities...
  Scored 4 opportunities
  Filtered to 3 with score >= 0.7
  Selected 2 within budget ($10.00)
```

### Шаг 3: Генерация контента

AI генерирует контент:
- **Статьи** - через Mistral (дешевле)
- **Код** - через OpenAI (лучше для кода)
- **SEO** - через Mistral

```
✍️ Generating: Need article about AI trends...
  ✅ Generated (850 tokens, $0.0017)
  Quality score: 0.85
```

### Шаг 4: Публикация

Отправка на платформы:
- Фриланс-платформы (Fiverr, Upwork)
- Контент-платформы (Medium, Dev.to)

```
📤 Publishing...
  ✅ published: $25.00 revenue
  💰 Profit: $24.98 (ROI: 1470.0%)
```

### Шаг 5-7: Финансы, обучение, реинвестирование

```
💰 Reinvesting profits...
  Reinvested $12.49 (50% of $24.98 profit)
  New budget: $22.49
```

## 📈 Отчёты и аналитика

### Отчёт по циклу

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 SELFBOT CYCLE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 OPPORTUNITIES
├─ Discovered: 4
├─ Evaluated: 4
└─ Selected: 2

✍️ CONTENT GENERATION
├─ Generated: 2
├─ Approved: 2
├─ Average Quality: 0.83
└─ Total Tokens: 1700

📤 PUBLISHING
├─ Submitted: 2
├─ Successful: 2
└─ Success Rate: 100.0%

💰 FINANCIALS
├─ Revenue: $45.00
├─ Costs: $0.04
├─ Profit: $44.96
└─ ROI: 1124.0%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Отчёт по оптимизации

```
🧠 STRATEGY OPTIMIZATION REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 OPPORTUNITY SELECTION
├─ Preferred Type: article
├─ Min Score: 0.75
├─ Focus On: article, seo_content
└─ Avoid: None

🤖 AI PROVIDER RECOMMENDATIONS
├─ article: mistral (avg profit: $22.50)
├─ code: openai (avg profit: $35.00)

💡 IMPROVEMENT SUGGESTIONS
1. Focus more on article - 90% success rate
2. Consider content_market_demo as primary source

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🎮 Интеграция с Telegram Bot

Управление через Telegram:

```
/selfbot - Запустить/остановить SelfBot
/selfbot_status - Статус работы
/selfbot_stats - Статистика заработка
/selfbot_report - Получить отчёт
/selfbot_budget <amount> - Установить бюджет
```

## 🔧 Настройка и оптимизация

### Настройка сканеров

```python
# Добавить свои RSS-фиды
SELFBOT_RSS_FEEDS=https://example.com/feed1,https://example.com/feed2
```

### Настройка стратегии

```python
# Минимальная оценка возможности
SELFBOT_MIN_OPPORTUNITY_SCORE=0.7

# Максимум возможностей за цикл
SELFBOT_MAX_OPPORTUNITIES_PER_CYCLE=5
```

### Настройка бюджета

```python
# Начальный бюджет
SELFBOT_INITIAL_BUDGET=10.00

# Процент реинвестирования
SELFBOT_REINVEST_PERCENTAGE=50  # 50% прибыли обратно в работу
```

## 📊 База данных

SelfBot использует отдельную БД `data/selfbot.db` с таблицами:

- **selfbot_opportunities** - найденные возможности
- **selfbot_generated_content** - сгенерированный контент
- **selfbot_publish_results** - результаты публикации
- **selfbot_learning** - данные обучения

## 🧪 Режим демо

По умолчанию SelfBot работает в **DEMO режиме**:
- Генерирует моковые возможности
- Симулирует публикацию (не отправляет реально)
- Безопасно для тестирования

Для продакшена:
1. Подключите реальные RSS-фиды
2. Настройте API фриланс-платформ
3. Настройте API контент-платформ (Medium, Dev.to)

## 🚀 Production Deployment

### Настройка для продакшена:

```env
SELFBOT_AUTO_PUBLISH=true           # Включить авто-публикацию
SELFBOT_REQUIRE_APPROVAL=false      # Не требовать одобрения
SELFBOT_INITIAL_BUDGET=100.00       # Больший бюджет
SELFBOT_SCAN_INTERVAL=1800          # Каждые 30 минут
```

### Запуск как сервис (systemd):

```ini
[Unit]
Description=SelfEarnBot - AI Content Arbitrage
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/robot
ExecStart=/usr/bin/python3 -m selfbot.main
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📈 Ожидаемые результаты

### Первая неделя (консервативно):
- Начальный бюджет: $10
- Среднее число операций в день: 10
- Средняя прибыль на операцию: $5
- **Прибыль за неделю**: ~$350

### Через месяц (с реинвестированием):
- Бюджет вырастет до: ~$200
- Операций в день: ~50
- **Прибыль за месяц**: ~$7,500

*Результаты зависят от качества источников, настроек и рыночных условий.*

## ⚠️ Важные замечания

1. **Начните с малого бюджета** ($5-10) для тестирования
2. **Проверяйте качество** первых генераций вручную
3. **Включайте авто-публикацию** только после тестирования
4. **Мониторьте результаты** через отчёты
5. **Оптимизируйте стратегию** на основе данных обучения

## 🤝 Содействие проекту

SelfBot - часть основного проекта Earning Robot. Вклады приветствуются:

1. Новые сканеры (парсеры платформ)
2. Новые генераторы (типы контента)
3. Новые издатели (платформы)
4. Улучшения алгоритмов оценки
5. Оптимизация стратегий

## 📄 Лицензия

MIT License - часть проекта Earning Robot

---

**🎯 Готовы к автономному заработку? Запустите бота!**

```bash
python selfbot/main.py
```

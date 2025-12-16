# System Architecture

This document provides a visual overview of the Earning Robot architecture.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     EARNING ROBOT SYSTEM                     │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐          ┌──────────────────┐
│  👤 USERS        │          │  👑 OWNER        │
│  (Customers)     │          │  (You)           │
└────────┬─────────┘          └────────┬─────────┘
         │                              │
         │                              │
    ┌────▼──────────────────────────────▼────┐
    │         🤖 EARNING ROBOT                │
    │  ┌──────────────────────────────────┐  │
    │  │   💬 Telegram Bot Interface      │  │
    │  │   - Command processing           │  │
    │  │   - Owner authentication         │  │
    │  │   - Automated notifications      │  │
    │  └──────────────────────────────────┘  │
    │                                         │
    │  ┌──────────────────────────────────┐  │
    │  │   🌐 REST API Server (Flask)     │  │
    │  │   - HTTP endpoints               │  │
    │  │   - Task execution               │  │
    │  │   - Statistics & reporting       │  │
    │  └──────────────────────────────────┘  │
    │                                         │
    │  ┌──────────────────────────────────┐  │
    │  │   🤖 AI Manager                  │  │
    │  │   - OpenAI integration           │  │
    │  │   - Mistral AI integration       │  │
    │  │   - Cost calculation             │  │
    │  └──────────────────────────────────┘  │
    │                                         │
    │  ┌──────────────────────────────────┐  │
    │  │   💰 Payment Processor           │  │
    │  │   - Stripe integration           │  │
    │  │   - Subscription management      │  │
    │  │   - Webhook handling             │  │
    │  └──────────────────────────────────┘  │
    │                                         │
    │  ┌──────────────────────────────────┐  │
    │  │   📊 Report Generator            │  │
    │  │   - Daily/weekly/monthly reports │  │
    │  │   - Financial analytics          │  │
    │  │   - Category breakdowns          │  │
    │  └──────────────────────────────────┘  │
    │                                         │
    │  ┌──────────────────────────────────┐  │
    │  │   📅 Task Scheduler              │  │
    │  │   - Automated reports            │  │
    │  │   - Health checks                │  │
    │  │   - Periodic tasks               │  │
    │  └──────────────────────────────────┘  │
    │                                         │
    │  ┌──────────────────────────────────┐  │
    │  │   🗄️ Database (SQLite)           │  │
    │  │   - Users & subscriptions        │  │
    │  │   - Tasks & results              │  │
    │  │   - Transactions & financials    │  │
    │  └──────────────────────────────────┘  │
    └─────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼────┐ ┌───▼────┐ ┌───▼────┐
    │ OpenAI  │ │Mistral │ │ Stripe │
    │   API   │ │  API   │ │  API   │
    └─────────┘ └────────┘ └────────┘
```

## Data Flow

### User Request Flow

```
1. User sends question via Telegram
                ↓
2. Telegram Bot receives message
                ↓
3. Create Task record in database
                ↓
4. Send request to AI Provider (OpenAI/Mistral)
                ↓
5. Receive AI response
                ↓
6. Update Task with result & cost
                ↓
7. Record API cost as expense
                ↓
8. Send response to user
                ↓
9. Log transaction
```

### Payment Flow

```
1. Customer wants subscription
                ↓
2. System creates Stripe checkout session
                ↓
3. Customer pays via Stripe
                ↓
4. Stripe sends webhook notification
                ↓
5. System verifies webhook signature
                ↓
6. Record income transaction
                ↓
7. Update user subscription status
                ↓
8. Send confirmation to customer
```

### Automated Report Flow

```
Scheduler triggers (daily at 09:00)
                ↓
Query database for transactions
                ↓
Calculate income, expenses, profit
                ↓
Generate category breakdowns
                ↓
Format report text
                ↓
Send via Telegram to owner
```

## Component Interactions

```
┌─────────────────────────────────────────────────────┐
│                    main.py                          │
│              (Main Entry Point)                     │
└───┬─────────────────┬─────────────────┬────────────┘
    │                 │                 │
    │ Thread 1        │ Thread 2        │ Main Thread
    │                 │                 │
┌───▼──────────┐ ┌───▼──────────┐ ┌───▼──────────┐
│ Flask Server │ │  Scheduler   │ │ Telegram Bot │
│              │ │              │ │              │
│ - REST API   │ │ - Reports    │ │ - Commands   │
│ - Webhooks   │ │ - Health     │ │ - Messages   │
└───┬──────────┘ └───┬──────────┘ └───┬──────────┘
    │                │                 │
    └────────┬───────┴────────┬────────┘
             │                │
        ┌────▼────────────────▼────┐
        │    Shared Components     │
        │                          │
        │  • Database              │
        │  • AI Manager            │
        │  • Payment Processor     │
        │  • Report Generator      │
        └──────────────────────────┘
```

## Database Schema

```
┌─────────────────┐
│     Users       │
├─────────────────┤
│ • id            │
│ • telegram_id   │
│ • email         │
│ • subscription  │
│ • expires       │
│ • created_at    │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐       ┌──────────────────┐
│     Tasks       │       │   Transactions   │
├─────────────────┤       ├──────────────────┤
│ • id            │       │ • id             │
│ • user_id       │       │ • user_id        │
│ • type          │       │ • type           │
│ • provider      │       │ • category       │
│ • input         │       │ • amount         │
│ • output        │       │ • description    │
│ • tokens_used   │       │ • status         │
│ • cost          │       │ • created_at     │
│ • status        │       └──────────────────┘
│ • created_at    │
└─────────────────┘
```

## File Organization

```
robot/
│
├── 🚀 Entry Points
│   ├── main.py              # Start all components
│   ├── cli.py               # Interactive CLI
│   ├── start.sh             # Linux/Mac launcher
│   └── start.bat            # Windows launcher
│
├── 🔧 Backend
│   ├── config.py            # Configuration loader
│   ├── database.py          # Data models & ORM
│   ├── app.py               # Flask REST API
│   ├── ai_providers.py      # AI integrations
│   └── scheduler.py         # Task automation
│
├── 💰 Billing
│   ├── payment_processor.py # Stripe integration
│   └── reporting.py         # Financial reports
│
├── 💬 Frontend
│   └── telegram_bot.py      # Telegram interface
│
├── 🧪 Tests
│   └── test_basic.py        # Unit tests
│
├── 📚 Documentation
│   ├── README.md            # Main guide
│   ├── QUICKSTART.md        # Quick setup
│   ├── INSTALLATION.md      # Install guide
│   ├── API_DOCUMENTATION.md # API reference
│   ├── EXAMPLES.md          # Usage examples
│   ├── DOCKER.md            # Docker guide
│   ├── FAQ.md               # FAQ
│   └── ARCHITECTURE.md      # This file
│
└── 🐳 Deployment
    ├── Dockerfile           # Container image
    ├── docker-compose.yml   # Docker orchestration
    └── requirements.txt     # Python dependencies
```

## Technology Stack

```
┌────────────────────────────────────────┐
│         Application Layer               │
│  Python 3.8+, Flask, Telegram Bot      │
└────────────────────────────────────────┘
                   ↓
┌────────────────────────────────────────┐
│         Integration Layer               │
│  OpenAI SDK, Mistral SDK, Stripe SDK   │
└────────────────────────────────────────┘
                   ↓
┌────────────────────────────────────────┐
│         Data Layer                      │
│  SQLAlchemy ORM, SQLite Database       │
└────────────────────────────────────────┘
                   ↓
┌────────────────────────────────────────┐
│         Infrastructure Layer            │
│  Docker, Linux/Windows, Cloud/VPS      │
└────────────────────────────────────────┘
```

## API Endpoints Map

```
/health
  └─ GET    → Health check

/api/task
  ├─ POST   → Create & execute task
  └─ GET    → Get task by ID
      └─ /{task_id}

/api/tasks
  └─ GET    → List tasks (with filters)

/api/report
  └─ GET    → Financial reports
      └─ /{daily|weekly|monthly}

/api/stats
  └─ GET    → System statistics

/api/payment
  ├─ /subscription
  │   └─ POST → Create subscription
  ├─ /micro
  │   └─ POST → Create micro-payment
  └─ /webhook
      └─ /stripe
          └─ POST → Handle Stripe webhooks
```

## Telegram Bot Commands

```
User Commands:
  /start    → Initialize bot
  /help     → Show help
  /ask      → Ask AI question
  /status   → System status
  [message] → Direct AI query

Owner Commands:
  /report   → Financial report
  /settings → Configuration
  /stats    → Statistics
```

## Security Layers

```
┌──────────────────────────────────────┐
│  1. Owner Authentication             │
│     - Telegram ID verification       │
└──────────────────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│  2. API Security                     │
│     - Webhook signatures             │
│     - Environment-based secrets      │
└──────────────────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│  3. Data Security                    │
│     - SQLAlchemy ORM (SQL injection) │
│     - Input validation               │
└──────────────────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│  4. Payment Security                 │
│     - Stripe hosted checkout         │
│     - PCI compliance                 │
└──────────────────────────────────────┘
```

## Deployment Scenarios

### Scenario 1: Local Development
```
Laptop → Python → SQLite → Local APIs
```

### Scenario 2: VPS Production
```
VPS → systemd → Python → SQLite → Public APIs
```

### Scenario 3: Docker Deployment
```
Server → Docker → Container → Python → APIs
```

### Scenario 4: Cloud Platform
```
Cloud → Managed Service → Containers → APIs
```

## Scaling Strategy

```
Single Instance (Start Here)
         ↓
Load Balancer + Multiple Instances
         ↓
Database Separation (PostgreSQL)
         ↓
Redis Caching Layer
         ↓
Message Queue (Celery/RabbitMQ)
         ↓
Microservices Architecture
```

## Monitoring Points

```
1. Application Metrics
   - Request rate
   - Response time
   - Error rate

2. Business Metrics
   - Tasks processed
   - Revenue generated
   - API costs

3. System Metrics
   - CPU usage
   - Memory usage
   - Disk space

4. External Services
   - AI API status
   - Stripe status
   - Telegram status
```

## Cost Breakdown

```
Revenue (Income)
  ├─ Subscriptions (recurring)
  └─ Micro-payments (per-task)

Expenses (Costs)
  ├─ OpenAI API ($0.002/1K tokens)
  ├─ Mistral API ($0.0002/1K tokens)
  ├─ Stripe fees (2.9% + $0.30)
  ├─ Infrastructure (VPS/Cloud)
  └─ Domain & SSL (optional)

Profit = Revenue - Expenses
```

## Extensibility Points

Want to add features? Here's where:

```
New AI Provider
  → backend/ai_providers.py
    └─ Add new provider class

New Payment Gateway
  → billing/payment_processor.py
    └─ Add new processor class

New Telegram Command
  → frontend/telegram_bot.py
    └─ Add command handler

New API Endpoint
  → backend/app.py
    └─ Add Flask route

New Report Type
  → billing/reporting.py
    └─ Add report method

New Database Model
  → backend/database.py
    └─ Add SQLAlchemy model
```

---

**This architecture enables:**
- ✅ Autonomous operation
- ✅ Easy scaling
- ✅ Simple maintenance
- ✅ Clear extensibility
- ✅ Robust monitoring
- ✅ Profitable operation

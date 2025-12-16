# 🤖 Earning Robot

An autonomous AI-powered earning robot that operates through a laptop, phone, and internet connection. The robot accepts user requests, executes tasks using external AI APIs, automatically handles payments, and generates financial reports.

## 🌟 Features

- **🤖 AI Task Automation**: Execute tasks using OpenAI and Mistral AI APIs
- **💬 Telegram Bot Control**: Full control via Telegram from your phone
- **🌐 REST API**: HTTP API for programmatic access
- **💰 Automated Payments**: Stripe integration for subscriptions and micro-payments
- **📊 Financial Reporting**: Automatic daily/weekly/monthly income and expense reports
- **📈 Analytics**: Track tasks, costs, and revenue in real-time
- **🔔 Notifications**: Automated alerts and reports via Telegram
- **🗄️ Database**: SQLite for easy deployment and accounting

## 📁 Project Structure

```
robot/
├── backend/              # Core backend logic
│   ├── app.py           # Flask REST API server
│   ├── config.py        # Configuration management
│   ├── database.py      # Database models and ORM
│   ├── ai_providers.py  # AI API integrations
│   └── scheduler.py     # Automated task scheduler
├── frontend/            # User interfaces
│   └── telegram_bot.py  # Telegram bot interface
├── billing/             # Payment and financial logic
│   ├── payment_processor.py  # Stripe payment integration
│   └── reporting.py     # Financial report generation
├── docs/                # Documentation
├── tests/               # Test files
├── .env.example         # Example environment variables
├── .gitignore          # Git ignore rules
├── requirements.txt     # Python dependencies
├── main.py             # Main entry point
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram account
- Stripe account (for payments)
- OpenAI and/or Mistral AI API keys

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/NickScherbakov/robot.git
   cd robot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and credentials
   ```

4. **Set up your Telegram bot**
   - Talk to [@BotFather](https://t.me/botfather) on Telegram
   - Create a new bot and get your bot token
   - Add the token to `.env` as `TELEGRAM_BOT_TOKEN`
   - Get your Telegram user ID (use [@userinfobot](https://t.me/userinfobot))
   - Add your user ID to `.env` as `TELEGRAM_OWNER_ID`

5. **Configure API keys**
   - Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
   - Get your Mistral API key from [Mistral AI](https://mistral.ai/)
   - Get your Stripe keys from [Stripe Dashboard](https://dashboard.stripe.com/)
   - Add all keys to your `.env` file

### Running the Robot

**Run all components together:**
```bash
python main.py
```

**Or run components separately:**

```bash
# Run Flask API server
python backend/app.py

# Run Telegram bot
python frontend/telegram_bot.py

# Run scheduler
python backend/scheduler.py
```

## 📱 Using the Telegram Bot

Once the bot is running, you can control it via Telegram:

### Available Commands

**User Commands:**
- `/start` - Initialize the bot
- `/help` - Show help information
- `/ask <question>` - Ask AI a question
- `/status` - Check robot status

**Owner Commands (restricted to owner):**
- `/report [daily|weekly|monthly]` - Get financial report
- `/settings` - Configure robot settings

### Examples

```
/ask What is the capital of France?
/ask Explain quantum computing in simple terms
/status
/report daily
```

You can also send regular messages without commands - they will be treated as AI questions.

## 🌐 REST API

The Flask server provides a REST API on `http://localhost:5000`

### Endpoints

#### Health Check
```bash
GET /health
```

#### Execute AI Task
```bash
POST /api/task
Content-Type: application/json

{
  "prompt": "Your question here",
  "provider": "openai",  // or "mistral"
  "user_id": "user@example.com"  // optional
}
```

#### Get Task Status
```bash
GET /api/task/{task_id}
```

#### List Tasks
```bash
GET /api/tasks?status=completed&limit=10
```

#### Get Financial Report
```bash
GET /api/report/daily    // or weekly, monthly
```

#### Get Statistics
```bash
GET /api/stats
```

#### Create Subscription
```bash
POST /api/payment/subscription
Content-Type: application/json

{
  "email": "customer@example.com"
}
```

### API Examples

**Using curl:**
```bash
# Ask AI a question
curl -X POST http://localhost:5000/api/task \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is AI?", "provider": "openai"}'

# Get daily report
curl http://localhost:5000/api/report/daily

# Check statistics
curl http://localhost:5000/api/stats
```

**Using Python:**
```python
import requests

# Execute AI task
response = requests.post('http://localhost:5000/api/task', json={
    'prompt': 'Explain machine learning',
    'provider': 'openai'
})
result = response.json()
print(result['response'])

# Get report
report = requests.get('http://localhost:5000/api/report/daily').json()
print(f"Profit: ${report['profit']}")
```

## 💰 Payment Configuration

### Subscription Model

The robot supports two payment models:

1. **Monthly Subscription** - Regular recurring payment
   - Configured via `SUBSCRIPTION_MONTHLY_PRICE` in `.env`
   - Default: $29.99/month

2. **Micro-payments** - Pay per task/operation
   - Configured via `MICRO_PAYMENT_PRICE` in `.env`
   - Default: $0.50 per operation

### Stripe Setup

1. Create a [Stripe account](https://stripe.com/)
2. Get your API keys from the Dashboard
3. Add keys to `.env`:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_WEBHOOK_SECRET` (for webhook verification)

### Webhook Configuration

For production, configure Stripe webhooks:
1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://yourdomain.com/api/webhook/stripe`
3. Select events: `checkout.session.completed`, `invoice.paid`, `invoice.payment_failed`
4. Copy webhook signing secret to `.env`

## 📊 Financial Reporting

### Automated Reports

The robot automatically generates and sends reports via Telegram:

- **Daily Report**: Sent every day at configured time (default 09:00 UTC)
- **Weekly Report**: Sent every Monday
- **Monthly Report**: Available on demand via `/report monthly`

### Report Contents

Reports include:
- Total income
- Total expenses
- Net profit/loss
- Breakdown by category (subscriptions, API costs, etc.)
- Trend analysis

### Manual Reports

Request reports anytime via Telegram:
```
/report daily
/report weekly
/report monthly
```

## 🔧 Configuration

All configuration is done via environment variables in `.env`:

### Required Settings
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_OWNER_ID=your_telegram_id
```

### Optional Settings
```env
# AI API Keys (at least one recommended)
OPENAI_API_KEY=your_openai_key
MISTRAL_API_KEY=your_mistral_key

# Payment Gateway (optional)
STRIPE_SECRET_KEY=your_stripe_key
STRIPE_PUBLISHABLE_KEY=your_publishable_key

# Application
DATABASE_PATH=data/robot.db
SECRET_KEY=your_secret_key

# Pricing
SUBSCRIPTION_MONTHLY_PRICE=29.99
MICRO_PAYMENT_PRICE=0.50

# Reporting
REPORT_TIME=09:00
TIMEZONE=UTC

# Server
HOST=0.0.0.0
PORT=5000
```

## 📈 Monitoring & Logs

### System Status

Check system status:
- Via Telegram: `/status`
- Via API: `GET /api/stats`

### Health Checks

The scheduler automatically checks system health every hour and sends alerts if:
- More than 5 tasks fail within an hour
- System resources are low
- API errors increase

### Logging

All components log to console. To save logs to file:
```bash
python main.py >> logs/robot.log 2>&1
```

## 🧪 Testing

Run tests (if you add them):
```bash
pytest tests/
```

## 🔒 Security

- API keys are stored in `.env` (never commit this file!)
- Telegram bot owner authentication
- Stripe webhook signature verification
- SQL injection protection via SQLAlchemy ORM

## 🚀 Deployment

### Local Deployment (Laptop)

Just run `python main.py` - the robot will run on your laptop.

### Cloud Deployment

**Deploy to Heroku:**
```bash
# Add Procfile
echo "web: python main.py" > Procfile

# Deploy
heroku create your-robot-name
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set TELEGRAM_OWNER_ID=your_id
# ... set other config vars
git push heroku main
```

**Deploy to VPS:**
```bash
# Install Python 3.8+
sudo apt update
sudo apt install python3 python3-pip

# Clone and setup
git clone https://github.com/NickScherbakov/robot.git
cd robot
pip3 install -r requirements.txt

# Configure .env
nano .env

# Run with supervisor or systemd
python3 main.py
```

### Running as a Service (Linux)

Create `/etc/systemd/system/earning-robot.service`:
```ini
[Unit]
Description=Earning Robot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/robot
ExecStart=/usr/bin/python3 /path/to/robot/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable earning-robot
sudo systemctl start earning-robot
sudo systemctl status earning-robot
```

## 📚 Extending the Robot

### Adding New AI Providers

1. Create a new provider class in `backend/ai_providers.py`:
```python
class NewAIProvider(AIProvider):
    def generate_response(self, prompt, max_tokens=500):
        # Implement API call
        return {'response': '...', 'tokens_used': 0, 'cost': 0.0}
```

2. Register in `AIManager`:
```python
self.providers['newai'] = NewAIProvider()
```

### Adding New Payment Gateways

1. Create a new processor in `billing/payment_processor.py`
2. Implement payment creation and webhook handling
3. Update configuration in `.env`

### Custom Task Types

Add new task types in `backend/database.py` and handle them in the API/bot.

## 🐛 Troubleshooting

### Bot not responding
- Check `TELEGRAM_BOT_TOKEN` is correct
- Verify bot is running: `ps aux | grep telegram_bot.py`
- Check logs for errors

### API errors
- Verify API keys are valid
- Check API rate limits
- Review error logs

### Database errors
- Ensure `data/` directory exists
- Check file permissions
- Database is created automatically on first run

### Payment issues
- Verify Stripe keys are correct
- Check webhook configuration
- Review Stripe dashboard for errors

## 📄 License

MIT License - see LICENSE file

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

- GitHub Issues: [Report a bug](https://github.com/NickScherbakov/robot/issues)
- Documentation: See `docs/` folder

## 🎯 Roadmap

- [ ] Add more AI providers (Claude, Gemini)
- [ ] Web dashboard UI
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] User management system
- [ ] Docker containerization
- [ ] Kubernetes deployment support

---

**Built with ❤️ for autonomous earning**
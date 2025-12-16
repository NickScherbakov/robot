# Quick Start Guide

Welcome to the Earning Robot! This guide will get you up and running in 5 minutes.

## Prerequisites Checklist

Before starting, make sure you have:

- [ ] Python 3.8 or higher installed
- [ ] Git installed
- [ ] A Telegram account
- [ ] At least one AI API key (OpenAI or Mistral)
- [ ] (Optional) Stripe account for payments

## 5-Minute Setup

### Step 1: Get the Code (30 seconds)

```bash
git clone https://github.com/NickScherbakov/robot.git
cd robot
```

### Step 2: Install Dependencies (1-2 minutes)

**On Linux/macOS:**
```bash
./start.sh
```

**On Windows:**
```bash
start.bat
```

**Or manually:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure (2 minutes)

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Get Telegram Bot Token:**
   - Open Telegram
   - Search for `@BotFather`
   - Send `/newbot` and follow instructions
   - Copy the token you receive

3. **Get your Telegram User ID:**
   - Search for `@userinfobot` in Telegram
   - Send `/start`
   - Copy your user ID

4. **Edit `.env` file:**
   ```bash
   nano .env  # or use any text editor
   ```
   
   Add your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_OWNER_ID=123456789
   OPENAI_API_KEY=sk-...  # Optional but recommended
   ```

### Step 4: Run (30 seconds)

```bash
python main.py
```

You should see:
```
╔═══════════════════════════════════════╗
║     🤖 EARNING ROBOT STARTING 🤖     ║
╚═══════════════════════════════════════╝
```

### Step 5: Test (30 seconds)

1. Open Telegram
2. Search for your bot (the name you gave to BotFather)
3. Send `/start`
4. Send `/ask What is AI?`

🎉 **Congratulations!** Your earning robot is now running!

## What's Running?

When you start the robot, three components run simultaneously:

1. **Flask API Server** (port 5000)
   - REST API endpoints
   - Available at: http://localhost:5000

2. **Telegram Bot**
   - Responds to your messages
   - Sends automated reports

3. **Task Scheduler**
   - Daily reports at 09:00 UTC
   - Weekly reports on Monday
   - Health checks every hour

## Your First Commands

Try these in Telegram:

```
/help              # Show all commands
/ask What is Python?    # Ask AI a question
/status            # Check robot status
/report daily      # Get today's financial report
```

Or just send a regular message - it will be processed as an AI query!

## Testing the API

Open a new terminal and try:

```bash
# Health check
curl http://localhost:5000/health

# Execute a task
curl -X POST http://localhost:5000/api/task \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is machine learning?"}'

# Get statistics
curl http://localhost:5000/api/stats
```

## Next Steps

Now that your robot is running:

1. **Read the full documentation:**
   - [README.md](README.md) - Complete guide
   - [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) - API reference
   - [EXAMPLES.md](docs/EXAMPLES.md) - Usage examples

2. **Configure payments (optional):**
   - Get Stripe API keys
   - Add them to `.env`
   - Start accepting payments!

3. **Customize:**
   - Adjust pricing in `.env`
   - Change report schedule
   - Add custom commands

4. **Deploy:**
   - See [INSTALLATION.md](docs/INSTALLATION.md) for production deployment

## Common Issues

### "Module not found" errors

Install dependencies:
```bash
pip install -r requirements.txt
```

### Bot not responding

Check that:
- `TELEGRAM_BOT_TOKEN` is correct in `.env`
- Bot is running (`python main.py`)
- You're messaging the correct bot

### API errors

Verify:
- Your API keys are valid
- You have API credits/quota
- Keys are correctly set in `.env`

### Port already in use

Change the port in `.env`:
```env
PORT=5001
```

## Getting Help

- 📖 Read the [full README](README.md)
- 💬 Check [examples](docs/EXAMPLES.md)
- 🐛 Report issues on [GitHub](https://github.com/NickScherbakov/robot/issues)

## What Can I Do With This?

The Earning Robot is perfect for:

✅ **Automated customer service** - Handle customer inquiries 24/7  
✅ **Content generation** - Create articles, summaries, translations  
✅ **Data analysis** - Process and analyze information  
✅ **Educational tutoring** - Answer questions, explain concepts  
✅ **Business automation** - Automate repetitive tasks  
✅ **Income generation** - Monetize AI capabilities  

## Cost Management

Monitor your costs:

```bash
# Via Telegram
/status

# Via API
curl http://localhost:5000/api/stats

# Via CLI
python cli.py
# Select option 4 (View Statistics)
```

## Stopping the Robot

Press `Ctrl+C` in the terminal where it's running.

## Restarting

Just run again:
```bash
python main.py
```

Your data is preserved in the `data/` directory.

---

**Ready to earn? Let's go! 🚀**

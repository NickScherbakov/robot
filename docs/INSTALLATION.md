# Installation Guide

## System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **RAM**: Minimum 512 MB
- **Disk Space**: 100 MB minimum
- **Internet**: Required for API access

## Step-by-Step Installation

### 1. Install Python

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### On macOS:
```bash
brew install python3
```

#### On Windows:
Download and install from [python.org](https://www.python.org/downloads/)

### 2. Clone the Repository

```bash
git clone https://github.com/NickScherbakov/robot.git
cd robot
```

### 3. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your favorite text editor and add your credentials:

```bash
nano .env  # or vim, code, etc.
```

**Minimum required configuration:**
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_OWNER_ID=123456789
```

### 6. Get API Keys

#### Telegram Bot Token:
1. Open Telegram
2. Search for @BotFather
3. Send `/newbot`
4. Follow instructions
5. Copy the token to `.env`

#### Telegram User ID:
1. Search for @userinfobot on Telegram
2. Send `/start`
3. Copy your ID to `.env`

#### OpenAI API Key (Optional but recommended):
1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Go to API Keys section
4. Create new secret key
5. Copy to `.env`

#### Mistral API Key (Optional):
1. Go to [mistral.ai](https://mistral.ai/)
2. Sign up
3. Get API key
4. Copy to `.env`

#### Stripe Keys (Optional - for payments):
1. Go to [stripe.com](https://stripe.com/)
2. Create account
3. Go to Developers → API Keys
4. Copy keys to `.env`

### 7. Initialize Database

The database is created automatically on first run, but you can test it:

```bash
python -c "from backend.database import Database; Database('data/robot.db').initialize(); print('Database OK')"
```

### 8. Test Configuration

```bash
python -c "from backend.config import Config; Config.validate(); print('Configuration OK')"
```

### 9. Run the Robot

```bash
python main.py
```

You should see:
```
╔═══════════════════════════════════════╗
║     🤖 EARNING ROBOT STARTING 🤖     ║
╚═══════════════════════════════════════╝
```

### 10. Test Telegram Bot

1. Open Telegram
2. Search for your bot (use the name you gave BotFather)
3. Send `/start`
4. Try `/ask What is AI?`

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt --upgrade
```

### Permission errors on Linux
```bash
chmod +x main.py
```

### Port already in use
Change the port in `.env`:
```env
PORT=5001
```

### Database errors
```bash
rm -rf data/
# Database will be recreated on next run
```

## Running in Production

### Using systemd (Linux)

1. Create service file:
```bash
sudo nano /etc/systemd/system/earning-robot.service
```

2. Add content:
```ini
[Unit]
Description=Earning Robot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/robot
Environment="PATH=/path/to/robot/venv/bin"
ExecStart=/path/to/robot/venv/bin/python /path/to/robot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable earning-robot
sudo systemctl start earning-robot
sudo systemctl status earning-robot
```

### Using Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t earning-robot .
docker run -d --env-file .env --name robot earning-robot
```

## Next Steps

- Read the [README.md](../README.md) for usage instructions
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

## Support

If you encounter issues:
1. Check the logs
2. Verify your API keys
3. Review [Troubleshooting](#troubleshooting) section
4. Open an issue on GitHub

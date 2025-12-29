# Usage Examples

This document provides practical examples of using the Earning Robot.

## Table of Contents

1. [Telegram Bot Examples](#telegram-bot-examples)
2. [REST API Examples](#rest-api-examples)
3. [CLI Examples](#cli-examples)
4. [Python SDK Examples](#python-sdk-examples)
5. [Common Workflows](#common-workflows)

## Telegram Bot Examples

### Basic AI Queries

```
User: /ask What is machine learning?
Bot: 🤔 Processing your request...
Bot: 🤖 AI Response:

Machine learning is a subset of artificial intelligence that enables computer systems to learn and improve from experience without being explicitly programmed...

📊 Tokens used: 125 | Cost: $0.0003
```

### Getting Status

```
User: /status
Bot: 🤖 Robot Status

📊 Tasks:
• Total: 150
• Completed: 145
• Failed: 2

👥 Users:
• Total: 25
• Active: 20

✅ System: Online
🕒 Time: 2025-01-15 10:30:00 UTC
```

### Owner Reports

```
User: /report daily
Bot: 📊 Daily Report - 2025-01-15

💰 Income: $150.00
💸 Expenses: $45.50
📈 Profit: $104.50
```

### Natural Language Interaction

```
User: Translate "Hello" to Spanish
Bot: 🤔 Processing your request...
Bot: 🤖 AI Response:

"Hello" in Spanish is "Hola".

📊 Tokens used: 15 | Cost: $0.00003
```

## REST API Examples

### Python

#### Execute AI Task

```python
import requests

url = "http://localhost:5000/api/task"
data = {
    "prompt": "Explain blockchain technology",
    "provider": "openai",
    "user_id": "john@example.com"
}

response = requests.post(url, json=data)
result = response.json()

print(f"Response: {result['response']}")
print(f"Cost: ${result['cost']:.4f}")
print(f"Tokens: {result['tokens_used']}")
```

#### Get Financial Report

```python
import requests

# Daily report
daily = requests.get("http://localhost:5000/api/report/daily").json()
print(f"Today's Profit: ${daily['profit']:.2f}")

# Weekly report
weekly = requests.get("http://localhost:5000/api/report/weekly").json()
print(f"Weekly Profit: ${weekly['profit']:.2f}")

# Monthly report
monthly = requests.get("http://localhost:5000/api/report/monthly").json()
print(f"Monthly Profit: ${monthly['profit']:.2f}")
```

#### Monitor Tasks

```python
import requests
import time

# Create a task
response = requests.post("http://localhost:5000/api/task", json={
    "prompt": "Write a haiku about coding"
})
task_id = response.json()['task_id']

# Check task status
while True:
    task = requests.get(f"http://localhost:5000/api/task/{task_id}").json()
    
    if task['status'] == 'completed':
        print(f"Task completed!")
        print(f"Output: {task['output']}")
        break
    elif task['status'] == 'failed':
        print(f"Task failed!")
        break
    
    time.sleep(1)
```

#### Batch Processing

```python
import requests
from concurrent.futures import ThreadPoolExecutor

def process_question(question):
    response = requests.post("http://localhost:5000/api/task", json={
        "prompt": question,
        "provider": "openai"
    })
    return response.json()

questions = [
    "What is Python?",
    "What is JavaScript?",
    "What is Go?",
    "What is Rust?"
]

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(process_question, questions)
    
    for result in results:
        print(f"Q: {result['task_id']}")
        print(f"A: {result['response'][:100]}...")
        print()
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

// Execute task
async function askAI(prompt) {
  const response = await axios.post('http://localhost:5000/api/task', {
    prompt: prompt,
    provider: 'openai'
  });
  
  return response.data;
}

// Get statistics
async function getStats() {
  const response = await axios.get('http://localhost:5000/api/stats');
  return response.data;
}

// Main
(async () => {
  // Ask a question
  const result = await askAI('What is Node.js?');
  console.log('Answer:', result.response);
  console.log('Cost:', result.cost);
  
  // Get stats
  const stats = await getStats();
  console.log('Total Tasks:', stats.tasks.total);
  console.log('Total Profit:', stats.financials.profit);
})();
```

### cURL

```bash
# Execute task
curl -X POST http://localhost:5000/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is REST API?",
    "provider": "openai"
  }'

# Get task
curl http://localhost:5000/api/task/1

# List completed tasks
curl "http://localhost:5000/api/tasks?status=completed&limit=5"

# Get daily report
curl http://localhost:5000/api/report/daily | jq .

# Get statistics
curl http://localhost:5000/api/stats | jq .
```

## CLI Examples

```bash
# Run CLI
python cli.py

# You'll see:
# ==================================================
# 🤖 EARNING ROBOT - CLI
# ==================================================
# 1. Execute AI Task
# 2. View Tasks
# 3. View Financial Report
# 4. View Statistics
# 5. List Users
# 6. View Transactions
# 0. Exit
# ==================================================

# Choose option 1 to execute a task:
Select option: 1
Enter your question: What is the meaning of life?
Provider (openai/mistral) [openai]: openai

# Choose option 3 for reports:
Select option: 3
1. Daily
2. Weekly
3. Monthly
Select report type: 1
```

## Python SDK Examples

### Direct Database Access

```python
from backend.database import Database, User, Task, Transaction
from backend.config import Config

# Initialize database
db = Database(Config.DATABASE_PATH).initialize()
session = db.get_session()

# Query users
users = session.query(User).filter_by(is_active=True).all()
for user in users:
    print(f"User: {user.email}, Subscription: {user.subscription_type}")

# Query tasks
from datetime import datetime, timedelta

yesterday = datetime.utcnow() - timedelta(days=1)
recent_tasks = session.query(Task).filter(
    Task.created_at >= yesterday
).all()

print(f"Tasks in last 24 hours: {len(recent_tasks)}")

session.close()
```

### Custom AI Integration

```python
from backend.ai_providers import AIManager
from backend.database import Database

ai_manager = AIManager()
db = Database().initialize()

# Use OpenAI
result = ai_manager.execute_task(
    "Explain Docker containers",
    provider='openai'
)
print(result['response'])

# Use Mistral
result = ai_manager.execute_task(
    "Explain Kubernetes",
    provider='mistral'
)
print(result['response'])
```

### Custom Reporting

```python
from billing.reporting import ReportGenerator
from backend.database import Database

db = Database().initialize()
session = db.get_session()

generator = ReportGenerator(session)

# Get custom date range
from datetime import date

summary = generator.get_daily_summary(date(2025, 1, 15))
print(f"Income on 2025-01-15: ${summary['income']}")

# Get category breakdown
breakdown = generator.get_category_breakdown(days=30)
print("Income sources:", breakdown['income_breakdown'])
print("Expense categories:", breakdown['expense_breakdown'])

session.close()
```

## Common Workflows

### Workflow 1: Set Up and Monitor

```bash
# 1. Start the robot
python main.py

# 2. In Telegram, send:
/start
/status

# 3. Ask your first question:
/ask What is artificial intelligence?

# 4. Check your first report:
/report daily
```

### Workflow 2: Automate Daily Tasks

```python
import requests
import schedule
import time

def daily_summary():
    """Get and print daily summary"""
    report = requests.get("http://localhost:5000/api/report/daily").json()
    print(f"📊 Daily Summary:")
    print(f"  Income: ${report['income']}")
    print(f"  Expenses: ${report['expenses']}")
    print(f"  Profit: ${report['profit']}")

def process_questions():
    """Process a batch of questions"""
    questions = [
        "Latest tech news summary",
        "Trending programming languages",
        "AI industry updates"
    ]
    
    for q in questions:
        result = requests.post("http://localhost:5000/api/task", json={
            "prompt": q
        }).json()
        print(f"Q: {q}")
        print(f"A: {result['response'][:200]}...")
        print()

# Schedule tasks
schedule.every().day.at("09:00").do(daily_summary)
schedule.every().day.at("10:00").do(process_questions)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Workflow 3: Customer Self-Service

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
ROBOT_API = "http://localhost:5000"

@app.route('/chat', methods=['POST'])
def chat():
    """Customer chat endpoint"""
    user_message = request.json['message']
    user_id = request.json['user_id']
    
    # Forward to robot
    response = requests.post(f"{ROBOT_API}/api/task", json={
        "prompt": user_message,
        "user_id": user_id,
        "provider": "openai"
    })
    
    return jsonify(response.json())

@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Create subscription"""
    email = request.json['email']
    
    response = requests.post(f"{ROBOT_API}/api/payment/subscription", json={
        "email": email
    })
    
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(port=8000)
```

## Advanced Examples

### Custom Scheduler Tasks

```python
from backend.scheduler import TaskScheduler
from apscheduler.triggers.cron import CronTrigger

class CustomScheduler(TaskScheduler):
    def custom_task(self):
        """Your custom scheduled task"""
        print("Running custom task!")
        # Your logic here
    
    def start(self):
        super().start()
        
        # Add custom schedule
        self.scheduler.add_job(
            self.custom_task,
            trigger=CronTrigger(hour=12, minute=0),
            id='custom_task',
            name='My Custom Task'
        )

# Use custom scheduler
scheduler = CustomScheduler()
scheduler.start()
```

### Integration with Other Services

```python
import requests
from backend.ai_providers import AIManager

# Slack integration example
def send_to_slack(message, webhook_url):
    requests.post(webhook_url, json={'text': message})

# Use robot to generate content
ai_manager = AIManager()
result = ai_manager.execute_task("Generate a motivational quote")

# Send to Slack
send_to_slack(
    f"Daily Quote: {result['response']}",
    "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
)
```

## Tips and Best Practices

1. **Rate Limiting**: Add delays between API calls to avoid hitting rate limits
2. **Error Handling**: Always wrap API calls in try-except blocks
3. **Cost Monitoring**: Regularly check `/api/stats` to monitor costs
4. **Batch Processing**: Use concurrent requests for better performance
5. **Caching**: Cache frequently requested data to reduce costs
6. **Testing**: Use test mode or mock APIs during development

## Support

For more examples and help:
- Read the [API Documentation](API_DOCUMENTATION.md)
- Check the [README](../README.md)
- Open an issue on GitHub

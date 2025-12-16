# API Documentation

## Base URL

```
http://localhost:5000
```

For production, replace with your domain.

## Authentication

Currently, the API doesn't require authentication for basic endpoints. For production, consider adding API key authentication.

## Endpoints

### Health Check

Check if the API is running.

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

---

### Create Task

Execute an AI task.

**Request:**
```http
POST /api/task
Content-Type: application/json

{
  "prompt": "What is artificial intelligence?",
  "provider": "openai",
  "user_id": "user@example.com"
}
```

**Parameters:**
- `prompt` (required): The question or task for AI
- `provider` (optional): AI provider - "openai" or "mistral" (default: "openai")
- `user_id` (optional): User identifier (email or username)

**Response:**
```json
{
  "task_id": 1,
  "response": "Artificial intelligence (AI) is...",
  "tokens_used": 150,
  "cost": 0.0003,
  "provider": "openai"
}
```

**Status Codes:**
- 200: Success
- 400: Bad request (missing prompt)
- 500: Server error

---

### Get Task

Retrieve details of a specific task.

**Request:**
```http
GET /api/task/{task_id}
```

**Response:**
```json
{
  "id": 1,
  "status": "completed",
  "provider": "openai",
  "input": "What is artificial intelligence?",
  "output": "Artificial intelligence is...",
  "tokens_used": 150,
  "cost": 0.0003,
  "created_at": "2024-01-15T10:30:00.000000",
  "completed_at": "2024-01-15T10:30:05.000000"
}
```

**Status Codes:**
- 200: Success
- 404: Task not found

---

### List Tasks

Get a list of tasks with optional filtering.

**Request:**
```http
GET /api/tasks?status=completed&limit=10
```

**Query Parameters:**
- `status` (optional): Filter by status - "pending", "processing", "completed", "failed"
- `limit` (optional): Maximum number of results (default: 50)

**Response:**
```json
{
  "tasks": [
    {
      "id": 1,
      "status": "completed",
      "provider": "openai",
      "created_at": "2024-01-15T10:30:00.000000"
    }
  ]
}
```

---

### Get Report

Get financial report.

**Request:**
```http
GET /api/report/{report_type}
```

**Path Parameters:**
- `report_type`: "daily", "weekly", or "monthly"

**Response:**
```json
{
  "date": "2024-01-15",
  "income": 150.00,
  "expenses": 45.50,
  "profit": 104.50,
  "breakdown": {
    "income_breakdown": {
      "subscription": 120.00,
      "micro_payment": 30.00
    },
    "expense_breakdown": {
      "api_cost": 45.50
    }
  }
}
```

---

### Get Statistics

Get overall system statistics.

**Request:**
```http
GET /api/stats
```

**Response:**
```json
{
  "tasks": {
    "total": 150,
    "completed": 145,
    "total_tokens": 50000,
    "total_cost": 12.50
  },
  "users": {
    "total": 25,
    "subscriptions": 10
  },
  "financials": {
    "total_income": 450.00,
    "total_expenses": 125.00,
    "profit": 325.00
  }
}
```

---

### Create Subscription

Create a Stripe checkout session for subscription.

**Request:**
```http
POST /api/payment/subscription
Content-Type: application/json

{
  "email": "customer@example.com"
}
```

**Response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/..."
}
```

**Status Codes:**
- 200: Success
- 400: Missing email
- 500: Payment processing error

---

### Create Micro-Payment

Create a one-time payment checkout session.

**Request:**
```http
POST /api/payment/micro
Content-Type: application/json

{
  "user_id": 1,
  "description": "AI Task Processing"
}
```

**Response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/..."
}
```

---

### Stripe Webhook

Handle Stripe webhook events (used by Stripe, not for direct calling).

**Request:**
```http
POST /api/webhook/stripe
Stripe-Signature: t=...,v1=...

{
  "type": "checkout.session.completed",
  "data": {...}
}
```

**Response:**
```json
{
  "status": "success"
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": "Description of the error"
}
```

**Common Status Codes:**
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

Currently no rate limiting is implemented. For production, consider adding rate limiting middleware.

## Examples

### Python

```python
import requests

# Execute AI task
response = requests.post('http://localhost:5000/api/task', json={
    'prompt': 'Explain quantum computing',
    'provider': 'openai',
    'user_id': 'user@example.com'
})

if response.status_code == 200:
    result = response.json()
    print(f"AI Response: {result['response']}")
    print(f"Cost: ${result['cost']:.4f}")
else:
    print(f"Error: {response.json()['error']}")

# Get daily report
report = requests.get('http://localhost:5000/api/report/daily').json()
print(f"Today's profit: ${report['profit']}")

# Get statistics
stats = requests.get('http://localhost:5000/api/stats').json()
print(f"Total tasks: {stats['tasks']['total']}")
print(f"Total profit: ${stats['financials']['profit']}")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

// Execute AI task
async function askAI(prompt) {
  try {
    const response = await axios.post('http://localhost:5000/api/task', {
      prompt: prompt,
      provider: 'openai'
    });
    
    console.log('AI Response:', response.data.response);
    console.log('Cost:', response.data.cost);
  } catch (error) {
    console.error('Error:', error.response.data.error);
  }
}

// Get report
async function getReport() {
  const response = await axios.get('http://localhost:5000/api/report/daily');
  console.log('Profit:', response.data.profit);
}

askAI('What is machine learning?');
getReport();
```

### cURL

```bash
# Create task
curl -X POST http://localhost:5000/api/task \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is AI?", "provider": "openai"}'

# Get task
curl http://localhost:5000/api/task/1

# List tasks
curl "http://localhost:5000/api/tasks?status=completed&limit=5"

# Get daily report
curl http://localhost:5000/api/report/daily

# Get statistics
curl http://localhost:5000/api/stats
```

## WebSocket Support

WebSocket support is not currently implemented but could be added for real-time updates.

## Versioning

Current API version: v1

Future versions will be accessible via `/api/v2/...` etc.

## Support

For API support:
- GitHub Issues: [Report a bug](https://github.com/NickScherbakov/robot/issues)
- Documentation: [README.md](../README.md)

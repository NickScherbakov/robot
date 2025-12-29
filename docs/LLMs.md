# LLMs - Methods and Ways to Maximize Earnings

## 📌 Introduction

This document describes strategies for using various Large Language Models (LLM) in the context of the **Earning Robot** project to maximize income and optimize expenses. Key idea: **choose the right model for the right task** to minimize costs while maintaining quality.

---

## 🔥 Trending Models (Q4 2025)

Top Weekly models (source: OpenRouter):
https://openrouter.ai/models?fmt=table&order=top-weekly

<!-- BEGIN: OPENROUTER_TOP_WEEKLY -->
| # | Model | Provider | Weekly Tokens |
|---|--------------------------|-----------|----------------|
| 1 | Grok Code Fast 1 | x-ai | — |
| 2 | Gemini 2.5 Flash | google | — |
| 3 | Claude Sonnet 4.5 | anthropic | — |
| 4 | Grok 4.1 Fast (free) | x-ai | — |
| 5 | Claude Opus 4.5 | anthropic | — |
| 6 | gpt-oss-120b | openai | — |
| 7 | DeepSeek V3.2 | deepseek | — |
| 8 | Gemini 2.0 Flash | google | — |
| 9 | Gemini 2.5 Flash Lite | google | — |
| 10 | Grok 4 Fast | x-ai | — |
| 11 | Gemini 3 Pro Preview | google | — |
| 12 | Gemini 2.5 Pro | google | — |
| 13 | Grok 4.1 Fast | x-ai | — |
| 14 | MiMo-V2-Flash (free) | xiaomi | — |
| 15 | MiniMax M2 | minimax | — |
| 16 | DeepSeek V3 0324 | deepseek | — |
| 17 | KAT-Coder-Pro V1 (free) | kwalipilot | — |
| 18 | GPT-4o-mini | openai | — |
| 19 | Claude Haiku 4.5 | anthropic | — |
| 20 | DeepSeek R1T2 Chimera (free) | ringtech | — |
<!-- END: OPENROUTER_TOP_WEEKLY -->

Recommended defaults:
- Budget/high-volume: Gemini 2.5 Flash, Gemini 2.0 Flash, DeepSeek V3.2
- Coding: Grok Code Fast 1, DeepSeek V3.2
- Analysis/reasoning: Claude Sonnet 4.5, Claude Opus 4.5
- Fast/free-tier: Grok 4.1 Fast (free), Gemini 2.5 Flash Lite

Note: Pricing varies; use dynamic selection + per-request accounting.

## 💰 Strategy 1: Tiered Processing

```
MAXIMUM INCOME = (INCOME FROM TASKS × VOLUME OF TASKS) - AI COSTS

Optimization:
├─ Reduce AI costs (choose cheaper models)
├─ Increase task volume (parallelism, speed)
├─ Improve quality (right model for the task)
└─ Increase profit per task (more complex, premium tasks)
```

---

## 🧠 LLM Comparison

### Currently Supported Models

| Model | Provider | Cost (1K tokens) | Speed | Quality | Use Case |
|--------|-----------|----------------------|----------|----------|-----------|
| GPT-4o-mini | OpenAI | $0.00015 | Very fast | Excellent | Quick & medium tasks |
| GPT-4o | OpenAI | $0.005 | Fast | Outstanding | Complex tasks |
| Claude 3.5 Sonnet | Anthropic | $0.003 | Fast | Outstanding | Analysis & reasoning |
| Mistral-small | Mistral | $0.0006 | Fast | Good | Standard tasks |
| Mistral-large | Mistral | $0.002 | Fast | Excellent | Complex tasks |

### Planned Models (OpenRouter Integration)

| Model | Price via OpenRouter | Native Price | Savings |
|--------|----------------------|------------|----------|
| Gemini 2.0 Flash | $0.00010 | $0.00015 | 33% |
| Llama 3.3 70B | $0.0004 | N/A | ∞ (available) |
| DeepSeek V3 | $0.00014 | N/A | ∞ (available) |
| Qwen 2.5 72B | $0.0003 | N/A | ∞ (available) |

---

## 💰 Strategy 1: Tiered Processing

### Concept

Different tasks require different levels of intelligence. Use cheap models for simple tasks, expensive ones for complex tasks.

### Implementation

```python
class TieredLLMStrategy:
    """
    Tiered LLM selection strategy
    """
    
    def select_model(self, task: Task) -> str:
        """
        Select model based on task complexity
        """
        complexity = self.analyze_complexity(task)
        
        if complexity < 0.3:  # Simple task
            return "mistral-small"  # $0.0002 per 1K tokens
        elif complexity < 0.6:  # Medium task
            return "gpt-4o-mini"  # $0.00015 per 1K tokens
        elif complexity < 0.85:  # Complex task
            return "claude-3-5-sonnet"  # $0.003 per 1K tokens
        else:  # Very complex task
            return "gpt-4o"  # $0.005 per 1K tokens
    
    def analyze_complexity(self, task: Task) -> float:
        """
        Evaluate task complexity (0.0 - 1.0)
        """
        score = 0.0
        
        # Complexity factors
        score += len(task.prompt) / 10000  # Long prompts = more complex
        score += task.context_length / 100000
        
        # Keywords indicating complexity
        complex_keywords = ['analysis', 'synthesis', 'algorithm', 'optimization', 'reasoning']
        for keyword in complex_keywords:
            if keyword in task.prompt.lower():
                score += 0.2
        
        return min(score, 1.0)
```

### Potential Savings

```
Without optimization (GPT-4o-mini only):
- Cost: $0.00015 per 1K tokens
- 1000 tasks/day × 100 tokens = 100K tokens
- Expenses: $0.015/day = $0.45/month

With tiered strategy:
- 70% simple (Mistral-small): 70K tokens × $0.0002 = $0.014
- 20% medium (GPT-4o-mini): 20K tokens × $0.00015 = $0.003
- 10% complex (GPT-4o): 10K tokens × $0.005 = $0.05
- Expenses: $0.067/day = $2/month

WAIT! This is more expensive, but:
- Higher quality = higher income
- Ability to charge more for complex tasks
- ROI improves due to quality
```

### When to Use

✅ When you have diverse tasks  
✅ When quality affects income  
✅ When you can determine task complexity  

❌ When NOT all tasks are of the same complexity level  
❌ When NOT execution speed is critical  

---

## 💰 Strategy 2: Request Caching

### Concept

Many users ask similar questions. Instead of calling AI every time, cache the responses.

### Implementation

```python
import hashlib
from backend.database import Cache

class CachedLLMProvider:
    """
    LLM provider with caching
    """
    
    def __init__(self, base_provider):
        self.base_provider = base_provider
        self.cache = Cache()
    
    def generate_response(self, prompt: str, **kwargs) -> dict:
        """
        Generate response using cache if possible
        """
        # Create cache key
        cache_key = self._hash_prompt(prompt)
        
        # Check cache
        cached_response = self.cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for: {prompt[:50]}...")
            return {
                **cached_response,
                'from_cache': True,
                'cost': 0  # No cost from cache!
            }
        
        # Not in cache - get from AI
        response = self.base_provider.generate_response(prompt, **kwargs)
        
        # Save to cache (24 hours)
        self.cache.set(cache_key, response, ttl=86400)
        
        return {
            **response,
            'from_cache': False
        }
    
    def _hash_prompt(self, prompt: str) -> str:
        """
        Create hash of prompt for cache key
        """
        return hashlib.sha256(prompt.lower().encode()).hexdigest()
```

### Potential Savings

```
Without caching:
- 1000 requests/day
- All go to AI
- Expenses: ~$0.2/day

With caching (40% hit rate):
- 600 requests to AI (cost: ~$0.12)
- 400 from cache (cost: $0)
- Expenses: ~$0.12/day = 40% savings
- Saved: ~$1800/month!
```

### When to Use

✅ When there are repeating questions  
✅ When a small cache update delay is acceptable  
✅ When there is storage space (DB or Redis)  

❌ When NOT always up-to-date information is required  
❌ When NOT questions are very specific (low hit rate)  

---

## 💰 Strategy 3: Batch Processing

### Concept

Send multiple tasks simultaneously instead of one at a time. Some providers (like OpenRouter) offer discounts on batch requests.

### Implementation

```python
from collections import deque
import asyncio

class BatchLLMProcessor:
    """
    Process tasks in batches for optimization
    """
    
    def __init__(self, batch_size=10, batch_timeout=5):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.queue = deque()
        self.running = False
    
    async def add_task(self, prompt: str) -> dict:
        """
        Add task to batch queue
        """
        future = asyncio.Future()
        self.queue.append({
            'prompt': prompt,
            'future': future
        })
        
        # If batch is full - process immediately
        if len(self.queue) >= self.batch_size:
            await self.process_batch()
        
        return await future
    
    async def process_batch(self):
        """
        Process batch of tasks
        """
        if not self.queue:
            return
        
        batch = []
        while self.queue and len(batch) < self.batch_size:
            batch.append(self.queue.popleft())
        
        # Send all prompts in one request (if API supports)
        prompts = [item['prompt'] for item in batch]
        
        # Parallel processing through batch API
        responses = await self._batch_request(prompts)
        
        # Distribute results
        for item, response in zip(batch, responses):
            item['future'].set_result(response)
    
    async def _batch_request(self, prompts: list) -> list:
        """
        Send batch request to AI provider
        """
        # This can be implemented depending on the provider
        # OpenRouter, for example, supports parallel requests
        tasks = [
            asyncio.create_task(self._single_request(p))
            for p in prompts
        ]
        return await asyncio.gather(*tasks)
```

### Potential Savings

```
Without batching:
- 100 requests
- Each request: $0.002
- Expenses: $0.20

With batching (4 batches of 25 requests):
- Initial requests: 4
- Batch discount: 20-30%
- With 25% discount: $0.002 × 0.75 = $0.0015
- Expenses: $0.15

Savings: 25-30%
```

### When to Use

✅ When many tasks in queue  
✅ When AI provider supports batch processing  
✅ When a small delay is acceptable  

❌ When NOT instant result is required  
❌ When NOT tasks must be processed in specific order  

---

## 💰 Strategy 4: Local Models with Ollama

### Concept

Run local LLMs on your server. No API costs after initial setup. Perfect for standard tasks.

### Implementation

```python
import subprocess
import requests
import json

class LocalLLMProvider:
    """
    Local LLM provider via Ollama
    """
    
    def __init__(self, model_name="mistral"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434"
        self.ensure_model_running()
    
    def ensure_model_running(self):
        """
        Ensure model is running
        """
        try:
            # Check availability
            requests.get(f"{self.base_url}/api/tags", timeout=1)
        except:
            logger.info(f"Starting model {self.model_name}...")
            subprocess.Popen([
                "ollama", "run", self.model_name
            ])
            time.sleep(10)  # Wait for startup
    
    def generate_response(self, prompt: str, max_tokens=500) -> dict:
        """
        Generate response locally
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            data = response.json()
            
            return {
                'response': data['response'],
                'tokens_used': data.get('eval_count', 0),
                'cost': 0,  # No costs!
                'model': self.model_name,
                'source': 'local'
            }
        except Exception as e:
            logger.error(f"Local LLM error: {e}")
            raise
```

### Potential Savings

```
OpenAI GPT-4o-mini:
- Cost: $0.00015 per 1K tokens
- 100K tokens/month
- Expenses: $0.015/month

Ollama (local Mistral):
- Initial costs: $50-100 for better GPU
- Electricity: $10-20/month
- Expenses: $0.3-0.6/month (electricity)
- Payback period: 2-4 months

After payback: ≈99% savings on AI
```

### When to Use

✅ When local model is sufficient (Mistral 7B)  
✅ When you have GPU server  
✅ When high processing volume  
✅ When sensitive to API latency  

❌ When NOT maximum performance is needed (large models require powerful GPU)  
❌ When NOT no budget for GPU infrastructure  

---

## 💰 Strategy 5: Dynamic Provider Selection

### Concept

Choose a provider in real-time based on:
- Cost
- Quality
- Speed
- Availability

### Implementation

```python
class DynamicProviderSelector:
    """
    Dynamic selection of best provider
    """
    
    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider(),
            'mistral': MistralProvider(),
            'ollama': LocalLLMProvider(),
            'openrouter': OpenRouterProvider()
        }
        self.performance_metrics = {}
    
    def select_best_provider(self, task: Task, criteria='cost_quality') -> str:
        """
        Select best provider based on criteria
        """
        scores = {}
        
        for provider_name in self.providers:
            score = self._calculate_score(provider_name, task, criteria)
            scores[provider_name] = score
        
        # Select provider with maximum score
        best_provider = max(scores, key=scores.get)
        logger.info(f"Selected provider: {best_provider} (score: {scores[best_provider]:.2f})")
        
        return best_provider
    
    def _calculate_score(self, provider_name: str, task: Task, criteria: str) -> float:
        """
        Calculate provider score
        """
        metrics = self.performance_metrics.get(provider_name, {})
        
        if criteria == 'cost':
            # Simply select by price
            return 1.0 / metrics.get('avg_cost', 0.01)
        
        elif criteria == 'speed':
            # Select by speed
            return 1.0 / metrics.get('avg_latency', 5)
        
        elif criteria == 'quality':
            # Select by quality (based on historical success)
            return metrics.get('success_rate', 0.5)
        
        elif criteria == 'cost_quality':
            # Select by cost/quality ratio
            cost = metrics.get('avg_cost', 0.01)
            quality = metrics.get('success_rate', 0.5)
            return quality / cost
        
        elif criteria == 'cost_speed':
            # Select by cost/speed ratio
            cost = metrics.get('avg_cost', 0.01)
            latency = metrics.get('avg_latency', 5)
            return (1.0 / latency) / cost
    
    def track_performance(self, provider_name: str, task_result: dict):
        """
        Track provider performance
        """
        if provider_name not in self.performance_metrics:
            self.performance_metrics[provider_name] = {
                'avg_cost': 0,
                'avg_latency': 0,
                'success_rate': 0,
                'total_tasks': 0
            }
        
        metrics = self.performance_metrics[provider_name]
        n = metrics['total_tasks'] + 1
        
        # Update average cost
        metrics['avg_cost'] = (
            (metrics['avg_cost'] * (n-1) + task_result['cost']) / n
        )
        
        # Update average latency
        metrics['avg_latency'] = (
            (metrics['avg_latency'] * (n-1) + task_result['latency']) / n
        )
        
        # Update success rate
        success = 1 if task_result['success'] else 0
        metrics['success_rate'] = (
            (metrics['success_rate'] * (n-1) + success) / n
        )
        
        metrics['total_tasks'] = n
```

### When to Use

✅ When there are multiple providers with different characteristics  
✅ When flexibility in choice is required  
✅ When providers have varying availability  

❌ When NOT locked to a specific provider  
❌ When NOT added complexity doesn't pay off  

---

## 📊 Recommended Combined Strategy

### Optimal Strategy for Earning Robot

```python
class OptimizedEarningStrategy:
    """
    Combined strategy for maximizing earnings
    """
    
    def __init__(self):
        # 1. Always use caching
        self.cache = CachedLLMProvider(BaseProvider())
        
        # 2. Dynamic provider selection
        self.selector = DynamicProviderSelector()
        
        # 3. Batching for large volumes
        self.batch_processor = BatchLLMProcessor()
        
        # 4. Local models for standard tasks
        self.local_provider = LocalLLMProvider()
    
    async def process_task(self, task: Task) -> dict:
        """
        Process task with optimization
        """
        # Step 1: Check cache
        cached = self.cache.get(task.prompt)
        if cached:
            return cached
        
        # Step 2: Determine complexity
        complexity = self.analyze_complexity(task)
        
        # Step 3: Select provider
        if complexity < 0.4:
            # Simple task - use local model
            provider = self.local_provider
        else:
            # Complex task - use best provider
            best_provider = self.selector.select_best_provider(
                task, criteria='cost_quality'
            )
            provider = self.providers[best_provider]
        
        # Step 4: Process through batching if many tasks
        if self.batch_processor.queue_size > 5:
            result = await self.batch_processor.add_task(task.prompt)
        else:
            result = provider.generate_response(task.prompt)
        
        # Step 5: Save to cache
        self.cache.set(task.prompt, result)
        
        # Step 6: Track performance
        self.selector.track_performance(
            provider.name,
            {**result, 'latency': ..., 'success': True}
        )
        
        return result
```

### Expected Results

```
Basic scenario (OpenAI GPT-4o-mini only):
├─ AI costs: $15/month
├─ Income: $1000/month
└─ Profit: $985/month

With optimization (combined strategy):
├─ Caching (40% saved): -$6
├─ Tiered processing (20% saved): -$2
├─ Local models (60% simple tasks): -$4
├─ Total saved: -$12
├─ AI costs: $3/month
├─ Income: $1200/month (higher quality)
└─ Profit: $1197/month (+21% ROI!)
```

---

## 🚀 Practical Implementation

### Step 1: Add OpenRouter Integration

```python
# backend/ai_providers.py

class OpenRouterProvider(AIProvider):
    """OpenRouter API integration"""
    
    def __init__(self):
        super().__init__()
        self.name = "openrouter"
        self.api_key = Config.OPENROUTER_API_KEY
        self.api_url = "https://openrouter.ai/api/v1"
    
    def generate_response(self, prompt: str, model: str = "deepseek-v3") -> dict:
        """Use OpenRouter for cheap requests"""
        response = requests.post(
            f"{self.api_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://earningrobot.com"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500
            }
        )
        
        data = response.json()
        
        return {
            'response': data['choices'][0]['message']['content'],
            'tokens_used': data['usage']['total_tokens'],
            'cost': 0.00014 * (data['usage']['total_tokens'] / 1000),  # DeepSeek V3 price
            'model': model
        }
```

### Step 2: Update Configuration

```env
# .env
OPENROUTER_API_KEY=sk-or-v1-xxxxx
ENABLE_CACHING=true
ENABLE_LOCAL_MODELS=false
OPTIMIZATION_STRATEGY=cost_quality
```

### Step 3: Integrate into Decision Engine

```python
# selfbot/brain/strategy.py

def get_optimal_model(self, task_type: str, budget: float) -> str:
    """
    Get optimal model based on task type and budget
    """
    if budget < 0.0001:
        return "gemini-2.0-flash"  # OpenRouter: $0.0001
    elif budget < 0.0003:
        return "deepseek-v3"  # OpenRouter: $0.00014
    elif budget < 0.003:
        return "mistral-large"  # Mistral: $0.002
    else:
        return "gpt-4o"  # OpenAI: maximum quality
```

---

## 📈 Metrics and Monitoring

### Key Metrics

```python
class LLMMetricsTracker:
    """
    Track LLM usage metrics
    """
    
    def track(self, task: Task, result: dict):
        """
        Log task metrics
        """
        metrics = {
            'timestamp': datetime.now(),
            'provider': result['model'],
            'prompt_tokens': result.get('prompt_tokens', 0),
            'completion_tokens': result.get('completion_tokens', 0),
            'total_tokens': result['tokens_used'],
            'cost': result['cost'],
            'latency': result.get('latency', 0),
            'cached': result.get('from_cache', False),
            'quality_score': self.evaluate_quality(result)
        }
        
        # Save to DB for analysis
        self.db.insert('llm_metrics', metrics)
    
    def get_daily_report(self) -> dict:
        """
        Get daily LLM usage report
        """
        metrics = self.db.query("""
            SELECT 
                provider,
                COUNT(*) as requests,
                SUM(cost) as total_cost,
                AVG(latency) as avg_latency,
                SUM(CASE WHEN cached=1 THEN 1 ELSE 0 END) as cache_hits,
                AVG(quality_score) as avg_quality
            FROM llm_metrics
            WHERE DATE(timestamp) = CURDATE()
            GROUP BY provider
        """)
        
        return metrics
```

---

## ⚠️ Important Notes

1. **Quality vs Cost**: The cheapest models don't always give the best ROI. Sometimes it's better to spend more on AI and get better results.

2. **Latency**: Local models are faster but require powerful GPU. OpenRouter can be faster in some cases.

3. **Reliability**: Always have a fallback provider in case the primary one is unavailable.

4. **Testing**: Test each strategy on your specific tasks, results may vary.

5. **Monitoring**: Regularly analyze metrics and adjust your strategy.

---

## 📚 Resources

- [OpenAI Pricing](https://openai.com/pricing)
- [Mistral AI Pricing](https://mistral.ai/pricing/)
- [OpenRouter](https://openrouter.ai) (Model aggregator)
- [Ollama](https://ollama.ai) (Local models)

---

**Last Updated**: December 2025  
**Author**: Earning Robot Team

⭐ Use these strategies to maximize your earnings!

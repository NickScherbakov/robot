"""
Model Optimizer - инструмент для оптимизации затрат на AI модели.

Аналог Google Cloud Vertex AI Model Optimizer.
Помогает выбрать наиболее экономичную модель для задачи,
отслеживает затраты и предлагает оптимизации.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics


@dataclass
class ModelPricing:
    """Цены на модель."""
    provider: str
    model: str
    input_price_per_1m: float  # USD за 1M входных токенов
    output_price_per_1m: float  # USD за 1M выходных токенов
    context_window: int
    capabilities: List[str]  # ['text', 'code', 'vision', 'function_calling']
    quality_score: float  # 0-100, оценка качества
    speed_score: float  # 0-100, оценка скорости
    last_updated: str


@dataclass
class UsageRecord:
    """Запись использования модели."""
    timestamp: str
    provider: str
    model: str
    task_type: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    success: bool
    quality_rating: Optional[float] = None  # Опциональная оценка качества результата


@dataclass
class OptimizationRecommendation:
    """Рекомендация по оптимизации."""
    current_model: str
    recommended_model: str
    estimated_savings_percent: float
    estimated_savings_usd_monthly: float
    quality_impact: str  # 'none', 'minimal', 'moderate', 'significant'
    reason: str
    confidence: float  # 0-1


class ModelOptimizer:
    """Оптимизатор моделей AI."""
    
    def __init__(self, db_path: str = "data/optimizer.db"):
        self.db_path = db_path
        self._init_database()
        self._load_model_pricing()
    
    def _init_database(self):
        """Инициализация базы данных."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица цен на модели
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_pricing (
                provider TEXT,
                model TEXT,
                input_price_per_1m REAL,
                output_price_per_1m REAL,
                context_window INTEGER,
                capabilities TEXT,
                quality_score REAL,
                speed_score REAL,
                last_updated TEXT,
                PRIMARY KEY (provider, model)
            )
        ''')
        
        # Таблица использования
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                provider TEXT,
                model TEXT,
                task_type TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                cost_usd REAL,
                latency_ms INTEGER,
                success INTEGER,
                quality_rating REAL
            )
        ''')
        
        # Таблица рекомендаций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                current_model TEXT,
                recommended_model TEXT,
                estimated_savings_percent REAL,
                estimated_savings_usd_monthly REAL,
                quality_impact TEXT,
                reason TEXT,
                confidence REAL,
                applied INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_model_pricing(self):
        """Загрузка актуальных цен на модели."""
        pricing_data = [
            # OpenAI
            ModelPricing("openai", "gpt-4o", 2.50, 10.00, 128000, 
                        ["text", "vision", "function_calling"], 95, 85, datetime.now().isoformat()),
            ModelPricing("openai", "gpt-4o-mini", 0.150, 0.600, 128000,
                        ["text", "vision", "function_calling"], 85, 95, datetime.now().isoformat()),
            ModelPricing("openai", "gpt-4-turbo", 10.00, 30.00, 128000,
                        ["text", "vision", "function_calling"], 98, 70, datetime.now().isoformat()),
            ModelPricing("openai", "gpt-3.5-turbo", 0.50, 1.50, 16385,
                        ["text", "function_calling"], 75, 98, datetime.now().isoformat()),
            
            # Anthropic
            ModelPricing("anthropic", "claude-3-opus-20240229", 15.00, 75.00, 200000,
                        ["text", "vision"], 98, 65, datetime.now().isoformat()),
            ModelPricing("anthropic", "claude-3-sonnet-20240229", 3.00, 15.00, 200000,
                        ["text", "vision"], 92, 80, datetime.now().isoformat()),
            ModelPricing("anthropic", "claude-3-haiku-20240307", 0.25, 1.25, 200000,
                        ["text", "vision"], 80, 95, datetime.now().isoformat()),
            
            # Mistral
            ModelPricing("mistral", "mistral-large-latest", 2.00, 6.00, 128000,
                        ["text", "function_calling"], 90, 85, datetime.now().isoformat()),
            ModelPricing("mistral", "mistral-medium-latest", 0.70, 2.10, 32000,
                        ["text"], 85, 90, datetime.now().isoformat()),
            ModelPricing("mistral", "mistral-small-latest", 0.20, 0.60, 32000,
                        ["text"], 78, 95, datetime.now().isoformat()),
            
            # Google
            ModelPricing("google", "gemini-1.5-pro", 1.25, 5.00, 2097152,
                        ["text", "vision", "code"], 93, 80, datetime.now().isoformat()),
            ModelPricing("google", "gemini-1.5-flash", 0.075, 0.30, 1048576,
                        ["text", "vision", "code"], 82, 98, datetime.now().isoformat()),
            
            # DeepSeek
            ModelPricing("deepseek", "deepseek-chat", 0.14, 0.28, 64000,
                        ["text", "code"], 88, 92, datetime.now().isoformat()),
            ModelPricing("deepseek", "deepseek-coder", 0.14, 0.28, 64000,
                        ["code"], 92, 90, datetime.now().isoformat()),
            
            # OpenRouter (агрегатор)
            ModelPricing("openrouter", "anthropic/claude-3.5-sonnet", 3.00, 15.00, 200000,
                        ["text", "vision"], 96, 82, datetime.now().isoformat()),
            ModelPricing("openrouter", "meta-llama/llama-3.1-70b-instruct", 0.52, 0.75, 131072,
                        ["text", "code"], 87, 88, datetime.now().isoformat()),
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pricing in pricing_data:
            cursor.execute('''
                INSERT OR REPLACE INTO model_pricing VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pricing.provider,
                pricing.model,
                pricing.input_price_per_1m,
                pricing.output_price_per_1m,
                pricing.context_window,
                json.dumps(pricing.capabilities),
                pricing.quality_score,
                pricing.speed_score,
                pricing.last_updated
            ))
        
        conn.commit()
        conn.close()
    
    def record_usage(self, record: UsageRecord):
        """Записать использование модели."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO usage_records 
            (timestamp, provider, model, task_type, input_tokens, output_tokens, 
             cost_usd, latency_ms, success, quality_rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.timestamp,
            record.provider,
            record.model,
            record.task_type,
            record.input_tokens,
            record.output_tokens,
            record.cost_usd,
            record.latency_ms,
            1 if record.success else 0,
            record.quality_rating
        ))
        
        conn.commit()
        conn.close()
    
    def calculate_cost(self, provider: str, model: str, 
                      input_tokens: int, output_tokens: int) -> float:
        """Рассчитать стоимость запроса."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT input_price_per_1m, output_price_per_1m
            FROM model_pricing
            WHERE provider = ? AND model = ?
        ''', (provider, model))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return 0.0
        
        input_price, output_price = result
        cost = (input_tokens / 1_000_000 * input_price + 
                output_tokens / 1_000_000 * output_price)
        return cost
    
    def get_cheapest_alternative(self, current_model: str, 
                                 required_capabilities: List[str],
                                 min_quality_score: float = 75) -> Optional[Tuple[str, str, float]]:
        """Найти самую дешевую альтернативу с нужными возможностями."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT provider, model, 
                   (input_price_per_1m + output_price_per_1m) as total_price,
                   capabilities, quality_score
            FROM model_pricing
            WHERE quality_score >= ?
            ORDER BY total_price ASC
        ''', (min_quality_score,))
        
        results = cursor.fetchall()
        conn.close()
        
        for provider, model, total_price, caps_json, quality in results:
            caps = json.loads(caps_json)
            if all(cap in caps for cap in required_capabilities):
                model_name = f"{provider}/{model}"
                if model_name != current_model:
                    return (provider, model, total_price)
        
        return None
    
    def get_usage_stats(self, days: int = 30) -> Dict:
        """Получить статистику использования за период."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Общие затраты
        cursor.execute('''
            SELECT SUM(cost_usd), COUNT(*), AVG(cost_usd)
            FROM usage_records
            WHERE timestamp >= ?
        ''', (since,))
        total_cost, total_requests, avg_cost = cursor.fetchone()
        
        # По моделям
        cursor.execute('''
            SELECT provider || '/' || model as model_name,
                   COUNT(*) as requests,
                   SUM(cost_usd) as cost,
                   AVG(latency_ms) as avg_latency,
                   AVG(quality_rating) as avg_quality
            FROM usage_records
            WHERE timestamp >= ?
            GROUP BY provider, model
            ORDER BY cost DESC
        ''', (since,))
        by_model = cursor.fetchall()
        
        # По типам задач
        cursor.execute('''
            SELECT task_type,
                   COUNT(*) as requests,
                   SUM(cost_usd) as cost
            FROM usage_records
            WHERE timestamp >= ?
            GROUP BY task_type
            ORDER BY cost DESC
        ''', (since,))
        by_task = cursor.fetchall()
        
        conn.close()
        
        return {
            "period_days": days,
            "total_cost_usd": total_cost or 0,
            "total_requests": total_requests or 0,
            "average_cost_per_request": avg_cost or 0,
            "by_model": [
                {
                    "model": row[0],
                    "requests": row[1],
                    "cost_usd": row[2],
                    "avg_latency_ms": row[3],
                    "avg_quality": row[4]
                }
                for row in by_model
            ],
            "by_task_type": [
                {
                    "task_type": row[0],
                    "requests": row[1],
                    "cost_usd": row[2]
                }
                for row in by_task
            ]
        }
    
    def analyze_and_recommend(self, days: int = 30) -> List[OptimizationRecommendation]:
        """Анализ использования и генерация рекомендаций."""
        recommendations = []
        stats = self.get_usage_stats(days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Анализируем каждую часто используемую модель
        for model_stat in stats["by_model"]:
            if model_stat["requests"] < 10:  # Мало данных
                continue
            
            current_model = model_stat["model"]
            provider, model = current_model.split("/")
            
            # Получаем возможности текущей модели
            cursor.execute('''
                SELECT capabilities, quality_score, 
                       input_price_per_1m, output_price_per_1m
                FROM model_pricing
                WHERE provider = ? AND model = ?
            ''', (provider, model))
            
            result = cursor.fetchone()
            if not result:
                continue
            
            capabilities = json.loads(result[0])
            current_quality = result[1]
            current_input_price = result[2]
            current_output_price = result[3]
            current_total_price = current_input_price + current_output_price
            
            # Ищем более дешевую альтернативу
            alternative = self.get_cheapest_alternative(
                current_model, 
                capabilities,
                min_quality_score=current_quality - 10  # Допускаем снижение качества на 10 пунктов
            )
            
            if alternative:
                alt_provider, alt_model, alt_price = alternative
                savings_percent = ((current_total_price - alt_price) / current_total_price) * 100
                
                if savings_percent > 10:  # Экономия больше 10%
                    monthly_savings = (model_stat["cost_usd"] / days) * 30 * (savings_percent / 100)
                    
                    # Определяем влияние на качество
                    cursor.execute('''
                        SELECT quality_score
                        FROM model_pricing
                        WHERE provider = ? AND model = ?
                    ''', (alt_provider, alt_model))
                    alt_quality = cursor.fetchone()[0]
                    
                    quality_diff = current_quality - alt_quality
                    if quality_diff <= 3:
                        quality_impact = "none"
                    elif quality_diff <= 7:
                        quality_impact = "minimal"
                    elif quality_diff <= 12:
                        quality_impact = "moderate"
                    else:
                        quality_impact = "significant"
                    
                    recommendation = OptimizationRecommendation(
                        current_model=current_model,
                        recommended_model=f"{alt_provider}/{alt_model}",
                        estimated_savings_percent=savings_percent,
                        estimated_savings_usd_monthly=monthly_savings,
                        quality_impact=quality_impact,
                        reason=f"Модель {alt_provider}/{alt_model} дешевле на {savings_percent:.1f}% при сопоставимом качестве",
                        confidence=0.8 if quality_impact in ["none", "minimal"] else 0.6
                    )
                    
                    recommendations.append(recommendation)
                    
                    # Сохраняем рекомендацию
                    cursor.execute('''
                        INSERT INTO recommendations
                        (timestamp, current_model, recommended_model, 
                         estimated_savings_percent, estimated_savings_usd_monthly,
                         quality_impact, reason, confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        datetime.now().isoformat(),
                        recommendation.current_model,
                        recommendation.recommended_model,
                        recommendation.estimated_savings_percent,
                        recommendation.estimated_savings_usd_monthly,
                        recommendation.quality_impact,
                        recommendation.reason,
                        recommendation.confidence
                    ))
        
        conn.commit()
        conn.close()
        
        return recommendations
    
    def get_optimal_model_for_task(self, task_type: str, 
                                   max_cost_per_request: Optional[float] = None,
                                   required_capabilities: Optional[List[str]] = None) -> Optional[Tuple[str, str]]:
        """Выбрать оптимальную модель для задачи."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Базовый запрос
        query = '''
            SELECT provider, model, quality_score, speed_score,
                   (input_price_per_1m + output_price_per_1m) as total_price,
                   capabilities
            FROM model_pricing
        '''
        
        conditions = []
        params = []
        
        if required_capabilities:
            # Фильтруем по возможностям позже, т.к. SQLite не поддерживает JSON функции напрямую
            pass
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        # Фильтруем и оцениваем
        candidates = []
        for provider, model, quality, speed, price, caps_json in results:
            caps = json.loads(caps_json)
            
            # Проверяем возможности
            if required_capabilities and not all(cap in caps for cap in required_capabilities):
                continue
            
            # Примерная стоимость запроса (1000 input + 500 output tokens)
            estimated_cost = (1000 / 1_000_000 * price * 0.4 + 
                            500 / 1_000_000 * price * 0.6)
            
            if max_cost_per_request and estimated_cost > max_cost_per_request:
                continue
            
            # Комплексная оценка: качество важнее, но цена тоже важна
            score = quality * 0.6 + speed * 0.2 - (price / 10) * 0.2
            
            candidates.append((provider, model, score))
        
        if not candidates:
            return None
        
        # Сортируем по оценке и возвращаем лучший
        candidates.sort(key=lambda x: x[2], reverse=True)
        return (candidates[0][0], candidates[0][1])
    
    def generate_optimization_report(self, days: int = 30) -> str:
        """Генерация отчета по оптимизации."""
        stats = self.get_usage_stats(days)
        recommendations = self.analyze_and_recommend(days)
        
        report = f"""
# 📊 Отчет по оптимизации использования AI моделей

## Период анализа: {days} дней

### Общая статистика
- **Общие затраты**: ${stats['total_cost_usd']:.2f}
- **Всего запросов**: {stats['total_requests']}
- **Средняя стоимость запроса**: ${stats['average_cost_per_request']:.4f}

### Использование по моделям
"""
        
        for model in stats['by_model'][:10]:  # Топ-10
            report += f"\n**{model['model']}**\n"
            report += f"- Запросов: {model['requests']}\n"
            report += f"- Затраты: ${model['cost_usd']:.2f}\n"
            report += f"- Средняя задержка: {model['avg_latency_ms']:.0f}ms\n"
            if model['avg_quality']:
                report += f"- Средняя оценка качества: {model['avg_quality']:.1f}/10\n"
        
        if recommendations:
            report += f"\n\n### 💡 Рекомендации по оптимизации ({len(recommendations)})\n"
            
            total_savings = sum(r.estimated_savings_usd_monthly for r in recommendations)
            report += f"\n**Потенциальная экономия: ${total_savings:.2f}/месяц**\n"
            
            for i, rec in enumerate(recommendations, 1):
                report += f"\n{i}. **{rec.current_model}** → **{rec.recommended_model}**\n"
                report += f"   - Экономия: {rec.estimated_savings_percent:.1f}% (${rec.estimated_savings_usd_monthly:.2f}/мес)\n"
                report += f"   - Влияние на качество: {rec.quality_impact}\n"
                report += f"   - Причина: {rec.reason}\n"
                report += f"   - Уверенность: {rec.confidence:.0%}\n"
        else:
            report += "\n\n### ✅ Рекомендации\nТекущее использование уже оптимально!\n"
        
        report += f"\n\n---\n*Отчет сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return report


# Пример использования
if __name__ == "__main__":
    optimizer = ModelOptimizer()
    
    # Примеры записи использования
    record1 = UsageRecord(
        timestamp=datetime.now().isoformat(),
        provider="openai",
        model="gpt-4o",
        task_type="content_generation",
        input_tokens=1500,
        output_tokens=800,
        cost_usd=0.035,
        latency_ms=2500,
        success=True,
        quality_rating=9.0
    )
    optimizer.record_usage(record1)
    
    # Получение статистики
    stats = optimizer.get_usage_stats(30)
    print(json.dumps(stats, indent=2))
    
    # Генерация рекомендаций
    recommendations = optimizer.analyze_and_recommend(30)
    for rec in recommendations:
        print(f"\n{rec.current_model} -> {rec.recommended_model}")
        print(f"Savings: {rec.estimated_savings_percent:.1f}% (${rec.estimated_savings_usd_monthly:.2f}/mo)")
    
    # Полный отчет
    report = optimizer.generate_optimization_report(30)
    print(report)

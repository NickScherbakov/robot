"""
REST API для Model Optimizer.

Предоставляет эндпоинты для:
- Получения рекомендаций по оптимизации
- Просмотра статистики использования
- Выбора оптимальной модели для задачи
- Управления ценами на модели
"""

from flask import Blueprint, jsonify, request
from backend.model_optimizer import ModelOptimizer, UsageRecord
from datetime import datetime
import os

# Создаем Blueprint для оптимизатора
optimizer_bp = Blueprint('optimizer', __name__, url_prefix='/api/optimizer')

# Инициализируем оптимизатор
db_path = os.getenv('OPTIMIZER_DB_PATH', 'data/optimizer.db')
optimizer = ModelOptimizer(db_path)


@optimizer_bp.route('/health', methods=['GET'])
def health():
    """Проверка здоровья сервиса."""
    return jsonify({
        "status": "healthy",
        "service": "model_optimizer",
        "timestamp": datetime.now().isoformat()
    })


@optimizer_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Получить статистику использования.
    
    Query params:
    - days: количество дней для анализа (default: 30)
    """
    days = request.args.get('days', 30, type=int)
    
    try:
        stats = optimizer.get_usage_stats(days)
        return jsonify({
            "success": True,
            "data": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@optimizer_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """
    Получить рекомендации по оптимизации.
    
    Query params:
    - days: количество дней для анализа (default: 30)
    """
    days = request.args.get('days', 30, type=int)
    
    try:
        recommendations = optimizer.analyze_and_recommend(days)
        
        return jsonify({
            "success": True,
            "count": len(recommendations),
            "total_potential_savings_monthly": sum(r.estimated_savings_usd_monthly for r in recommendations),
            "recommendations": [
                {
                    "current_model": r.current_model,
                    "recommended_model": r.recommended_model,
                    "estimated_savings_percent": r.estimated_savings_percent,
                    "estimated_savings_usd_monthly": r.estimated_savings_usd_monthly,
                    "quality_impact": r.quality_impact,
                    "reason": r.reason,
                    "confidence": r.confidence
                }
                for r in recommendations
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@optimizer_bp.route('/report', methods=['GET'])
def get_report():
    """
    Получить полный отчет по оптимизации в Markdown.
    
    Query params:
    - days: количество дней для анализа (default: 30)
    - format: формат ответа (markdown или json, default: json)
    """
    days = request.args.get('days', 30, type=int)
    format_type = request.args.get('format', 'json')
    
    try:
        report = optimizer.generate_optimization_report(days)
        
        if format_type == 'markdown':
            return report, 200, {'Content-Type': 'text/markdown; charset=utf-8'}
        else:
            return jsonify({
                "success": True,
                "report": report
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@optimizer_bp.route('/optimal-model', methods=['POST'])
def get_optimal_model():
    """
    Получить оптимальную модель для задачи.
    
    Request body:
    {
        "task_type": "content_generation",
        "max_cost_per_request": 0.01,  // optional
        "required_capabilities": ["text", "code"]  // optional
    }
    """
    data = request.get_json()
    
    if not data or 'task_type' not in data:
        return jsonify({
            "success": False,
            "error": "task_type is required"
        }), 400
    
    task_type = data['task_type']
    max_cost = data.get('max_cost_per_request')
    capabilities = data.get('required_capabilities', ['text'])
    
    try:
        result = optimizer.get_optimal_model_for_task(
            task_type=task_type,
            max_cost_per_request=max_cost,
            required_capabilities=capabilities
        )
        
        if result:
            provider, model = result
            
            # Получаем информацию о цене
            cost = optimizer.calculate_cost(provider, model, 1000, 500)
            
            return jsonify({
                "success": True,
                "provider": provider,
                "model": model,
                "estimated_cost_per_request": cost,
                "full_model_name": f"{provider}/{model}"
            })
        else:
            return jsonify({
                "success": False,
                "error": "No suitable model found for the given criteria"
            }), 404
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@optimizer_bp.route('/usage', methods=['POST'])
def record_usage():
    """
    Записать использование модели.
    
    Request body:
    {
        "provider": "openai",
        "model": "gpt-4o",
        "task_type": "content_generation",
        "input_tokens": 1500,
        "output_tokens": 800,
        "latency_ms": 2500,
        "success": true,
        "quality_rating": 9.0  // optional
    }
    """
    data = request.get_json()
    
    required_fields = ['provider', 'model', 'task_type', 'input_tokens', 
                       'output_tokens', 'latency_ms', 'success']
    
    if not all(field in data for field in required_fields):
        return jsonify({
            "success": False,
            "error": f"Missing required fields. Required: {required_fields}"
        }), 400
    
    try:
        # Рассчитываем стоимость
        cost = optimizer.calculate_cost(
            data['provider'],
            data['model'],
            data['input_tokens'],
            data['output_tokens']
        )
        
        # Создаем запись
        record = UsageRecord(
            timestamp=datetime.now().isoformat(),
            provider=data['provider'],
            model=data['model'],
            task_type=data['task_type'],
            input_tokens=data['input_tokens'],
            output_tokens=data['output_tokens'],
            cost_usd=cost,
            latency_ms=data['latency_ms'],
            success=data['success'],
            quality_rating=data.get('quality_rating')
        )
        
        optimizer.record_usage(record)
        
        return jsonify({
            "success": True,
            "cost_usd": cost,
            "timestamp": record.timestamp
        }), 201
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@optimizer_bp.route('/pricing', methods=['GET'])
def get_pricing():
    """
    Получить информацию о ценах на все модели.
    
    Query params:
    - provider: фильтр по провайдеру (optional)
    - min_quality: минимальный quality_score (optional)
    - max_price: максимальная общая цена (optional)
    """
    import sqlite3
    
    provider_filter = request.args.get('provider')
    min_quality = request.args.get('min_quality', type=float)
    max_price = request.args.get('max_price', type=float)
    
    try:
        conn = sqlite3.connect(optimizer.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT provider, model, input_price_per_1m, output_price_per_1m,
                   context_window, capabilities, quality_score, speed_score,
                   last_updated
            FROM model_pricing
            WHERE 1=1
        '''
        params = []
        
        if provider_filter:
            query += " AND provider = ?"
            params.append(provider_filter)
        
        if min_quality:
            query += " AND quality_score >= ?"
            params.append(min_quality)
        
        if max_price:
            query += " AND (input_price_per_1m + output_price_per_1m) <= ?"
            params.append(max_price)
        
        query += " ORDER BY provider, model"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        import json
        
        models = []
        for row in results:
            models.append({
                "provider": row[0],
                "model": row[1],
                "input_price_per_1m": row[2],
                "output_price_per_1m": row[3],
                "total_price_per_1m": row[2] + row[3],
                "context_window": row[4],
                "capabilities": json.loads(row[5]),
                "quality_score": row[6],
                "speed_score": row[7],
                "last_updated": row[8]
            })
        
        return jsonify({
            "success": True,
            "count": len(models),
            "models": models
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@optimizer_bp.route('/cost-calculator', methods=['POST'])
def calculate_cost():
    """
    Калькулятор стоимости запроса.
    
    Request body:
    {
        "provider": "openai",
        "model": "gpt-4o",
        "input_tokens": 1500,
        "output_tokens": 800
    }
    """
    data = request.get_json()
    
    required_fields = ['provider', 'model', 'input_tokens', 'output_tokens']
    
    if not all(field in data for field in required_fields):
        return jsonify({
            "success": False,
            "error": f"Missing required fields. Required: {required_fields}"
        }), 400
    
    try:
        cost = optimizer.calculate_cost(
            data['provider'],
            data['model'],
            data['input_tokens'],
            data['output_tokens']
        )
        
        if cost == 0:
            return jsonify({
                "success": False,
                "error": "Model not found in pricing database"
            }), 404
        
        return jsonify({
            "success": True,
            "provider": data['provider'],
            "model": data['model'],
            "input_tokens": data['input_tokens'],
            "output_tokens": data['output_tokens'],
            "cost_usd": cost,
            "cost_per_1k_tokens": cost / ((data['input_tokens'] + data['output_tokens']) / 1000)
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Регистрация Blueprint в основном приложении
def register_optimizer_api(app):
    """Регистрация API оптимизатора в Flask приложении."""
    app.register_blueprint(optimizer_bp)
    print("✅ Model Optimizer API registered at /api/optimizer")

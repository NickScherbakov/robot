"""
Flask REST API server for the Earning Robot.
Provides HTTP endpoints for task execution and management.
"""
from flask import Flask, request, jsonify
from backend.config import Config
from backend.database import Database, User, Task, Transaction
from backend.ai_providers import AIManager
from billing.payment_processor import PaymentProcessor
from billing.reporting import ReportGenerator
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize database
db = Database(Config.DATABASE_PATH).initialize()
ai_manager = AIManager()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/task', methods=['POST'])
def create_task():
    """
    Create and execute an AI task
    
    Request body:
    {
        "prompt": "Your question here",
        "provider": "openai" or "mistral",
        "user_id": "optional_user_identifier"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing prompt'}), 400
        
        prompt = data['prompt']
        provider = data.get('provider', 'openai')
        user_identifier = data.get('user_id')
        
        session = db.get_session()
        
        try:
            # Get or create user
            user = None
            if user_identifier:
                user = session.query(User).filter_by(email=user_identifier).first()
                if not user:
                    user = User(email=user_identifier)
                    session.add(user)
                    session.commit()
            
            # Create task record
            task = Task(
                user_id=user.id if user else None,
                task_type='completion',
                ai_provider=provider,
                input_text=prompt,
                status='processing'
            )
            session.add(task)
            session.commit()
            
            # Execute AI task
            result = ai_manager.execute_task(prompt, provider=provider)
            
            # Update task
            task.output_text = result['response']
            task.tokens_used = result['tokens_used']
            task.cost = result['cost']
            task.status = 'completed'
            task.completed_at = datetime.utcnow()
            session.commit()
            
            # Record expense
            payment_processor = PaymentProcessor(session)
            payment_processor.record_expense(
                amount=result['cost'],
                category='api_cost',
                description=f"{provider.upper()} API - {result['tokens_used']} tokens"
            )
            
            return jsonify({
                'task_id': task.id,
                'response': result['response'],
                'tokens_used': result['tokens_used'],
                'cost': result['cost'],
                'provider': provider
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get task details by ID"""
    session = db.get_session()
    
    try:
        task = session.query(Task).filter_by(id=task_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'id': task.id,
            'status': task.status,
            'provider': task.ai_provider,
            'input': task.input_text,
            'output': task.output_text,
            'tokens_used': task.tokens_used,
            'cost': task.cost,
            'created_at': task.created_at.isoformat(),
            'completed_at': task.completed_at.isoformat() if task.completed_at else None
        })
        
    finally:
        session.close()


@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    """List all tasks with optional filtering"""
    session = db.get_session()
    
    try:
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        query = session.query(Task)
        
        if status:
            query = query.filter_by(status=status)
        
        tasks = query.order_by(Task.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'tasks': [
                {
                    'id': task.id,
                    'status': task.status,
                    'provider': task.ai_provider,
                    'created_at': task.created_at.isoformat()
                }
                for task in tasks
            ]
        })
        
    finally:
        session.close()


@app.route('/api/report/<report_type>', methods=['GET'])
def get_report(report_type):
    """
    Get financial report
    
    report_type: daily, weekly, or monthly
    """
    if report_type not in ['daily', 'weekly', 'monthly']:
        return jsonify({'error': 'Invalid report type'}), 400
    
    session = db.get_session()
    
    try:
        generator = ReportGenerator(session)
        
        if report_type == 'daily':
            report = generator.get_daily_summary()
        elif report_type == 'weekly':
            report = generator.get_weekly_summary()
        else:
            report = generator.get_monthly_summary()
        
        # Add category breakdown
        report['breakdown'] = generator.get_category_breakdown(
            7 if report_type == 'weekly' else 30
        )
        
        return jsonify(report)
        
    finally:
        session.close()


@app.route('/api/payment/subscription', methods=['POST'])
def create_subscription():
    """Create a subscription checkout session"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        session = db.get_session()
        
        try:
            # Get or create user
            user = session.query(User).filter_by(email=email).first()
            if not user:
                user = User(email=email)
                session.add(user)
                session.commit()
            
            # Create payment session
            payment_processor = PaymentProcessor(session)
            checkout_url = payment_processor.create_subscription(user, email)
            
            return jsonify({
                'checkout_url': checkout_url
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/payment/micro', methods=['POST'])
def create_micro_payment():
    """Create a micro-payment checkout session"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        description = data.get('description', 'AI Task Processing')
        
        session = db.get_session()
        
        try:
            user = None
            if user_id:
                user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            payment_processor = PaymentProcessor(session)
            checkout_url = payment_processor.create_micro_payment(user, description)
            
            return jsonify({
                'checkout_url': checkout_url
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error creating micro-payment: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    session = db.get_session()
    
    try:
        payment_processor = PaymentProcessor(session)
        success = payment_processor.handle_webhook(payload, sig_header)
        
        if success:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error'}), 400
            
    finally:
        session.close()


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get overall statistics"""
    session = db.get_session()
    
    try:
        from sqlalchemy import func
        
        # Task statistics
        total_tasks = session.query(Task).count()
        completed_tasks = session.query(Task).filter_by(status='completed').count()
        total_tokens = session.query(func.sum(Task.tokens_used)).scalar() or 0
        total_api_cost = session.query(func.sum(Task.cost)).scalar() or 0.0
        
        # User statistics
        total_users = session.query(User).count()
        active_subscriptions = session.query(User).filter_by(
            subscription_type='monthly',
            is_active=True
        ).count()
        
        # Financial statistics
        total_income = session.query(func.sum(Transaction.amount)).filter_by(
            transaction_type='income',
            status='completed'
        ).scalar() or 0.0
        
        total_expenses = session.query(func.sum(Transaction.amount)).filter_by(
            transaction_type='expense',
            status='completed'
        ).scalar() or 0.0
        
        return jsonify({
            'tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'total_tokens': total_tokens,
                'total_cost': round(total_api_cost, 2)
            },
            'users': {
                'total': total_users,
                'subscriptions': active_subscriptions
            },
            'financials': {
                'total_income': round(total_income, 2),
                'total_expenses': round(total_expenses, 2),
                'profit': round(total_income - total_expenses, 2)
            }
        })
        
    finally:
        session.close()


if __name__ == '__main__':
    logger.info("🚀 Starting Flask API server...")
    app.run(host=Config.HOST, port=Config.PORT, debug=True)

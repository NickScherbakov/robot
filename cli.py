"""
Simple command-line interface for the Earning Robot.
For testing and manual operations.
"""
from backend.database import Database, User, Task, Transaction
from backend.ai_providers import AIManager
from backend.config import Config
from billing.reporting import ReportGenerator
from billing.payment_processor import PaymentProcessor
from backend.model_optimizer import ModelOptimizer
import sys


def show_menu():
    """Display main menu"""
    print("\n" + "="*50)
    print("🤖 EARNING ROBOT - CLI")
    print("="*50)
    print("1. Execute AI Task")
    print("2. View Tasks")
    print("3. View Financial Report")
    print("4. View Statistics")
    print("5. List Users")
    print("6. View Transactions")
    print("7. 📊 Model Optimizer - Stats")
    print("8. 💡 Model Optimizer - Recommendations")
    print("9. 📝 Model Optimizer - Full Report")
    print("0. Exit")
    print("="*50)


def execute_ai_task(db, ai_manager):
    """Execute an AI task"""
    print("\n--- Execute AI Task ---")
    prompt = input("Enter your question: ")
    provider = input("Provider (openai/mistral) [openai]: ").strip() or "openai"
    
    try:
        print("\n🤔 Processing...")
        result = ai_manager.execute_task(prompt, provider=provider)
        
        print(f"\n✅ Response:\n{result['response']}")
        print(f"\n📊 Tokens: {result['tokens_used']} | Cost: ${result['cost']:.4f}")
        
        # Save task
        session = db.get_session()
        task = Task(
            task_type='cli',
            ai_provider=provider,
            input_text=prompt,
            output_text=result['response'],
            tokens_used=result['tokens_used'],
            cost=result['cost'],
            status='completed'
        )
        session.add(task)
        
        # Record expense
        processor = PaymentProcessor(session)
        processor.record_expense(
            amount=result['cost'],
            category='api_cost',
            description=f"{provider.upper()} API - CLI"
        )
        
        session.commit()
        session.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def view_tasks(db):
    """View recent tasks"""
    print("\n--- Recent Tasks ---")
    session = db.get_session()
    
    tasks = session.query(Task).order_by(Task.created_at.desc()).limit(10).all()
    
    if not tasks:
        print("No tasks found.")
    else:
        for task in tasks:
            print(f"\nTask #{task.id} - {task.status}")
            print(f"Provider: {task.ai_provider}")
            print(f"Input: {task.input_text[:50]}...")
            if task.output_text:
                print(f"Output: {task.output_text[:50]}...")
            print(f"Cost: ${task.cost:.4f} | Tokens: {task.tokens_used}")
            print(f"Created: {task.created_at}")
    
    session.close()


def view_report(db):
    """View financial report"""
    print("\n--- Financial Report ---")
    print("1. Daily")
    print("2. Weekly")
    print("3. Monthly")
    
    choice = input("Select report type: ")
    
    report_types = {'1': 'daily', '2': 'weekly', '3': 'monthly'}
    report_type = report_types.get(choice, 'daily')
    
    session = db.get_session()
    generator = ReportGenerator(session)
    report = generator.format_report(report_type)
    print(f"\n{report}")
    session.close()


def view_statistics(db):
    """View statistics"""
    print("\n--- Statistics ---")
    session = db.get_session()
    
    from sqlalchemy import func
    
    total_tasks = session.query(Task).count()
    completed_tasks = session.query(Task).filter_by(status='completed').count()
    total_cost = session.query(func.sum(Task.cost)).scalar() or 0.0
    
    total_income = session.query(func.sum(Transaction.amount)).filter_by(
        transaction_type='income', status='completed'
    ).scalar() or 0.0
    
    total_expenses = session.query(func.sum(Transaction.amount)).filter_by(
        transaction_type='expense', status='completed'
    ).scalar() or 0.0
    
    print(f"\n📊 Tasks:")
    print(f"  Total: {total_tasks}")
    print(f"  Completed: {completed_tasks}")
    print(f"  Total API Cost: ${total_cost:.2f}")
    
    print(f"\n💰 Financials:")
    print(f"  Income: ${total_income:.2f}")
    print(f"  Expenses: ${total_expenses:.2f}")
    print(f"  Profit: ${total_income - total_expenses:.2f}")
    
    session.close()


def list_users(db):
    """List all users"""
    print("\n--- Users ---")
    session = db.get_session()
    
    users = session.query(User).all()
    
    if not users:
        print("No users found.")
    else:
        for user in users:
            print(f"\nUser #{user.id}")
            print(f"  Email: {user.email or 'N/A'}")
            print(f"  Telegram: {user.telegram_id or 'N/A'}")
            print(f"  Subscription: {user.subscription_type}")
            print(f"  Active: {user.is_active}")
            print(f"  Created: {user.created_at}")
    
    session.close()


def view_transactions(db):
    """View recent transactions"""
    print("\n--- Recent Transactions ---")
    session = db.get_session()
    
    transactions = session.query(Transaction).order_by(
        Transaction.created_at.desc()
    ).limit(20).all()
    
    if not transactions:
        print("No transactions found.")
    else:
        for txn in transactions:
            symbol = "💰" if txn.transaction_type == 'income' else "💸"
            print(f"\n{symbol} Transaction #{txn.id}")
            print(f"  Type: {txn.transaction_type}")
            print(f"  Category: {txn.category}")
            print(f"  Amount: ${txn.amount:.2f}")
            print(f"  Description: {txn.description}")
            print(f"  Status: {txn.status}")
            print(f"  Created: {txn.created_at}")
    
    session.close()


def view_optimizer_stats(optimizer):
    """View Model Optimizer statistics"""
    print("\n--- Model Optimizer Statistics ---")
    days = input("Period in days [30]: ").strip() or "30"
    
    try:
        days = int(days)
        stats = optimizer.get_usage_stats(days)
        
        print(f"\n📊 Usage Statistics ({days} days)")
        print(f"\nTotal Cost: ${stats['total_cost_usd']:.2f}")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Average Cost per Request: ${stats['average_cost_per_request']:.4f}")
        
        if stats['by_model']:
            print("\n💰 Top Models by Cost:")
            for i, model in enumerate(stats['by_model'][:5], 1):
                print(f"  {i}. {model['model']}")
                print(f"     Requests: {model['requests']} | Cost: ${model['cost_usd']:.2f}")
                if model['avg_latency_ms']:
                    print(f"     Avg Latency: {model['avg_latency_ms']:.0f}ms")
        
        if stats['by_task_type']:
            print("\n📋 By Task Type:")
            for task in stats['by_task_type']:
                print(f"  {task['task_type']}: {task['requests']} requests, ${task['cost_usd']:.2f}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


def view_optimizer_recommendations(optimizer):
    """View optimization recommendations"""
    print("\n--- Optimization Recommendations ---")
    days = input("Period in days [30]: ").strip() or "30"
    
    try:
        days = int(days)
        recommendations = optimizer.analyze_and_recommend(days)
        
        if not recommendations:
            print("\n✅ No recommendations - current usage is already optimal!")
            return
        
        total_savings = sum(r.estimated_savings_usd_monthly for r in recommendations)
        print(f"\n💡 Found {len(recommendations)} optimization opportunities")
        print(f"💰 Total Potential Savings: ${total_savings:.2f}/month")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec.current_model} → {rec.recommended_model}")
            print(f"   Savings: {rec.estimated_savings_percent:.1f}% (${rec.estimated_savings_usd_monthly:.2f}/mo)")
            print(f"   Quality Impact: {rec.quality_impact}")
            print(f"   Reason: {rec.reason}")
            print(f"   Confidence: {rec.confidence:.0%}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


def view_optimizer_report(optimizer):
    """View full optimization report"""
    print("\n--- Full Optimization Report ---")
    days = input("Period in days [30]: ").strip() or "30"
    
    try:
        days = int(days)
        report = optimizer.generate_optimization_report(days)
        print(report)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main CLI loop"""
    print("\n🤖 Initializing Earning Robot CLI...")
    
    # Initialize database
    db = Database(Config.DATABASE_PATH).initialize()
    ai_manager = AIManager()
    optimizer = ModelOptimizer()
    
    print("✅ Ready!")
    
    while True:
        show_menu()
        choice = input("\nSelect option: ").strip()
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        elif choice == '1':
            execute_ai_task(db, ai_manager)
        elif choice == '2':
            view_tasks(db)
        elif choice == '3':
            view_report(db)
        elif choice == '4':
            view_statistics(db)
        elif choice == '5':
            list_users(db)
        elif choice == '6':
            view_transactions(db)
        elif choice == '7':
            view_optimizer_stats(optimizer)
        elif choice == '8':
            view_optimizer_recommendations(optimizer)
        elif choice == '9':
            view_optimizer_report(optimizer)
        else:
            print("\n❌ Invalid option. Please try again.")
    
    db.close()


if __name__ == '__main__':
    main()

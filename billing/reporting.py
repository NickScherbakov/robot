"""
Financial reporting module for the Earning Robot.
Generates income/expense reports and analytics.
"""
from sqlalchemy import func
from backend.database import Transaction
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates financial reports"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def get_daily_summary(self, date=None):
        """
        Get daily financial summary
        
        Args:
            date: Date to generate report for (defaults to today)
            
        Returns:
            Dictionary with income, expenses, and profit
        """
        if not date:
            date = datetime.utcnow().date()
        
        start_time = datetime.combine(date, datetime.min.time())
        end_time = datetime.combine(date, datetime.max.time())
        
        # Calculate income
        income = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'income',
            Transaction.status == 'completed',
            Transaction.created_at >= start_time,
            Transaction.created_at <= end_time
        ).scalar() or 0.0
        
        # Calculate expenses
        expenses = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'expense',
            Transaction.status == 'completed',
            Transaction.created_at >= start_time,
            Transaction.created_at <= end_time
        ).scalar() or 0.0
        
        return {
            'date': date.isoformat(),
            'income': round(income, 2),
            'expenses': round(expenses, 2),
            'profit': round(income - expenses, 2)
        }
    
    def get_weekly_summary(self):
        """Get weekly financial summary"""
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        
        start_time = datetime.combine(week_ago, datetime.min.time())
        end_time = datetime.combine(today, datetime.max.time())
        
        income = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'income',
            Transaction.status == 'completed',
            Transaction.created_at >= start_time,
            Transaction.created_at <= end_time
        ).scalar() or 0.0
        
        expenses = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'expense',
            Transaction.status == 'completed',
            Transaction.created_at >= start_time,
            Transaction.created_at <= end_time
        ).scalar() or 0.0
        
        return {
            'period': 'last_7_days',
            'start_date': week_ago.isoformat(),
            'end_date': today.isoformat(),
            'income': round(income, 2),
            'expenses': round(expenses, 2),
            'profit': round(income - expenses, 2)
        }
    
    def get_monthly_summary(self):
        """Get monthly financial summary"""
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)
        
        start_time = datetime.combine(month_start, datetime.min.time())
        end_time = datetime.combine(today, datetime.max.time())
        
        income = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'income',
            Transaction.status == 'completed',
            Transaction.created_at >= start_time,
            Transaction.created_at <= end_time
        ).scalar() or 0.0
        
        expenses = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'expense',
            Transaction.status == 'completed',
            Transaction.created_at >= start_time,
            Transaction.created_at <= end_time
        ).scalar() or 0.0
        
        return {
            'period': 'current_month',
            'start_date': month_start.isoformat(),
            'end_date': today.isoformat(),
            'income': round(income, 2),
            'expenses': round(expenses, 2),
            'profit': round(income - expenses, 2)
        }
    
    def get_category_breakdown(self, days=30):
        """
        Get breakdown by category
        
        Args:
            days: Number of days to include
            
        Returns:
            Dictionary with category breakdowns
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Income by category
        income_by_category = self.db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.transaction_type == 'income',
            Transaction.status == 'completed',
            Transaction.created_at >= cutoff_date
        ).group_by(Transaction.category).all()
        
        # Expenses by category
        expense_by_category = self.db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.transaction_type == 'expense',
            Transaction.status == 'completed',
            Transaction.created_at >= cutoff_date
        ).group_by(Transaction.category).all()
        
        return {
            'income_breakdown': {cat: round(total, 2) for cat, total in income_by_category},
            'expense_breakdown': {cat: round(total, 2) for cat, total in expense_by_category}
        }
    
    def format_report(self, report_type='daily'):
        """
        Format a comprehensive report
        
        Args:
            report_type: Type of report (daily, weekly, monthly)
            
        Returns:
            Formatted text report
        """
        if report_type == 'daily':
            summary = self.get_daily_summary()
            title = f"📊 Daily Report - {summary['date']}"
        elif report_type == 'weekly':
            summary = self.get_weekly_summary()
            title = f"📊 Weekly Report - Last 7 Days"
        else:
            summary = self.get_monthly_summary()
            title = f"📊 Monthly Report - {summary['start_date']} to {summary['end_date']}"
        
        report = f"""
{title}

💰 Income: ${summary['income']:.2f}
💸 Expenses: ${summary['expenses']:.2f}
{'📈' if summary['profit'] >= 0 else '📉'} Profit: ${summary['profit']:.2f}
"""
        
        # Add category breakdown for weekly/monthly reports
        if report_type in ['weekly', 'monthly']:
            breakdown = self.get_category_breakdown(7 if report_type == 'weekly' else 30)
            
            if breakdown['income_breakdown']:
                report += "\n💵 Income Sources:\n"
                for category, amount in breakdown['income_breakdown'].items():
                    report += f"  • {category}: ${amount:.2f}\n"
            
            if breakdown['expense_breakdown']:
                report += "\n💳 Expenses:\n"
                for category, amount in breakdown['expense_breakdown'].items():
                    report += f"  • {category}: ${amount:.2f}\n"
        
        return report.strip()

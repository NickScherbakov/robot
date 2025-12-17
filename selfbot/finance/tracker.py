"""
Finance tracker for SelfBot operations.
Tracks all revenue, costs, and profits.
"""
from typing import Dict, Optional
from datetime import datetime
from selfbot.database.models import PublishResult
import logging

logger = logging.getLogger(__name__)


class FinanceTracker:
    """Tracks financial transactions for SelfBot"""
    
    def __init__(self, db_session):
        self.session = db_session
        self.current_budget = 0.0
        logger.info("FinanceTracker initialized")
    
    def set_budget(self, amount: float):
        """Set current available budget"""
        self.current_budget = amount
        logger.info(f"Budget set to ${amount:.2f}")
    
    def get_budget(self) -> float:
        """Get current available budget"""
        return self.current_budget
    
    def record_generation_cost(self, content_id: int, cost: float):
        """
        Record cost of generating content.
        
        Args:
            content_id: ID of generated content
            cost: Generation cost
        """
        self.current_budget -= cost
        logger.info(f"Recorded generation cost: ${cost:.4f} (remaining budget: ${self.current_budget:.2f})")
    
    def record_revenue(self, result_id: int, revenue: float):
        """
        Record revenue from published content.
        
        Args:
            result_id: ID of publish result
            revenue: Revenue amount
        """
        self.current_budget += revenue
        logger.info(f"Recorded revenue: ${revenue:.2f} (new budget: ${self.current_budget:.2f})")
    
    def calculate_roi(self, cost: float, revenue: float) -> float:
        """
        Calculate ROI (Return on Investment).
        
        Args:
            cost: Investment cost
            revenue: Revenue generated
            
        Returns:
            ROI as decimal (e.g., 0.5 = 50% ROI)
        """
        if cost == 0:
            return 0.0
        
        roi = (revenue - cost) / cost
        return round(roi, 4)
    
    def get_summary(self, since: Optional[datetime] = None) -> Dict:
        """
        Get financial summary.
        
        Args:
            since: Get summary since this date (None = all time)
            
        Returns:
            Summary dictionary
        """
        query = self.session.query(PublishResult)
        
        if since:
            query = query.filter(PublishResult.published_at >= since)
        
        results = query.all()
        
        total_revenue = sum(r.actual_revenue for r in results)
        total_cost = sum(r.actual_cost for r in results)
        total_profit = sum(r.actual_profit for r in results)
        
        successful = [r for r in results if r.status in ['accepted', 'earning', 'published']]
        
        return {
            'total_revenue': round(total_revenue, 2),
            'total_cost': round(total_cost, 2),
            'total_profit': round(total_profit, 2),
            'total_operations': len(results),
            'successful_operations': len(successful),
            'success_rate': round(len(successful) / len(results), 2) if results else 0,
            'average_roi': round(sum(r.roi for r in successful) / len(successful), 2) if successful else 0,
            'current_budget': round(self.current_budget, 2)
        }
    
    def check_budget_available(self, required: float) -> bool:
        """
        Check if budget is available for operation.
        
        Args:
            required: Required budget
            
        Returns:
            True if budget available
        """
        available = self.current_budget >= required
        if not available:
            logger.warning(f"Insufficient budget: need ${required:.2f}, have ${self.current_budget:.2f}")
        return available

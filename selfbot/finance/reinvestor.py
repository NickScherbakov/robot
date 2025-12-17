"""
Auto-reinvestment module.
Automatically reinvests profits to grow the operation.
"""
from typing import Dict
from selfbot.config import SelfBotConfig
import logging

logger = logging.getLogger(__name__)


class AutoReinvestor:
    """Handles automatic profit reinvestment"""
    
    def __init__(self, finance_tracker):
        self.tracker = finance_tracker
        self.config = SelfBotConfig
        logger.info("AutoReinvestor initialized")
    
    def should_reinvest(self, profit: float) -> bool:
        """
        Determine if profits should be reinvested.
        
        Args:
            profit: Recent profit amount
            
        Returns:
            True if should reinvest
        """
        if not self.config.AUTO_REINVEST:
            return False
        
        if profit <= 0:
            logger.info("No profit to reinvest")
            return False
        
        return True
    
    def calculate_reinvestment(self, profit: float) -> Dict:
        """
        Calculate reinvestment amounts.
        
        Args:
            profit: Profit to potentially reinvest
            
        Returns:
            Dictionary with reinvestment breakdown
        """
        if not self.should_reinvest(profit):
            return {
                'reinvest_amount': 0.0,
                'reserve_amount': profit,
                'reinvest_percentage': 0
            }
        
        reinvest_pct = self.config.REINVEST_PERCENTAGE
        reinvest_amount = (profit * reinvest_pct) / 100
        reserve_amount = profit - reinvest_amount
        
        return {
            'reinvest_amount': round(reinvest_amount, 2),
            'reserve_amount': round(reserve_amount, 2),
            'reinvest_percentage': reinvest_pct
        }
    
    def execute_reinvestment(self, profit: float) -> float:
        """
        Execute reinvestment by adding to budget.
        
        Args:
            profit: Profit to reinvest from
            
        Returns:
            Amount reinvested
        """
        calc = self.calculate_reinvestment(profit)
        reinvest_amount = calc['reinvest_amount']
        
        if reinvest_amount > 0:
            current_budget = self.tracker.get_budget()
            new_budget = current_budget + reinvest_amount
            self.tracker.set_budget(new_budget)
            
            logger.info(
                f"Reinvested ${reinvest_amount:.2f} ({calc['reinvest_percentage']}% of ${profit:.2f} profit)"
            )
            logger.info(f"New budget: ${new_budget:.2f}")
        
        return reinvest_amount
    
    def get_reinvestment_strategy(self, total_profit: float, operations_count: int) -> Dict:
        """
        Develop reinvestment strategy based on performance.
        
        Args:
            total_profit: Total profit so far
            operations_count: Number of operations completed
            
        Returns:
            Strategy recommendations
        """
        avg_profit_per_operation = total_profit / operations_count if operations_count > 0 else 0
        
        # If very profitable, consider increasing reinvestment
        if avg_profit_per_operation > 10.0:
            recommended_pct = min(self.config.REINVEST_PERCENTAGE + 10, 80)
            message = "High profitability - consider increasing reinvestment"
        elif avg_profit_per_operation > 5.0:
            recommended_pct = self.config.REINVEST_PERCENTAGE
            message = "Good profitability - maintain current reinvestment"
        else:
            recommended_pct = max(self.config.REINVEST_PERCENTAGE - 10, 30)
            message = "Lower profitability - consider decreasing reinvestment"
        
        return {
            'current_percentage': self.config.REINVEST_PERCENTAGE,
            'recommended_percentage': recommended_pct,
            'avg_profit_per_operation': round(avg_profit_per_operation, 2),
            'message': message
        }

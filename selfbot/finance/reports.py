"""
SelfBot-specific financial reports.
"""
from typing import Dict
from datetime import datetime, timedelta
from selfbot.database.models import PublishResult, GeneratedContent, Opportunity
import logging

logger = logging.getLogger(__name__)


class SelfBotReports:
    """Generates financial and performance reports for SelfBot"""
    
    def __init__(self, db_session):
        self.session = db_session
        logger.info("SelfBotReports initialized")
    
    def generate_cycle_report(self) -> str:
        """
        Generate report for current cycle.
        
        Returns:
            Formatted report string
        """
        # Get recent data (last 24 hours)
        since = datetime.utcnow() - timedelta(hours=24)
        
        opportunities = self.session.query(Opportunity).filter(
            Opportunity.created_at >= since
        ).all()
        
        content = self.session.query(GeneratedContent).filter(
            GeneratedContent.created_at >= since
        ).all()
        
        results = self.session.query(PublishResult).filter(
            PublishResult.published_at >= since
        ).all()
        
        # Calculate metrics
        total_revenue = sum(r.actual_revenue for r in results)
        total_cost = sum(r.actual_cost for r in results)
        total_profit = total_revenue - total_cost
        
        successful = [r for r in results if r.status in ['accepted', 'earning', 'published']]
        
        report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 SELFBOT CYCLE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 OPPORTUNITIES
├─ Discovered: {len(opportunities)}
├─ Evaluated: {sum(1 for o in opportunities if o.status == 'evaluated')}
└─ Selected: {sum(1 for o in opportunities if o.status == 'selected')}

✍️ CONTENT GENERATION
├─ Generated: {len(content)}
├─ Approved: {sum(1 for c in content if c.status == 'approved')}
├─ Average Quality: {(sum(c.quality_score or 0 for c in content) / len(content)):.2f if content else 0.00}
└─ Total Tokens: {sum(c.tokens_used for c in content)}

📤 PUBLISHING
├─ Submitted: {len(results)}
├─ Successful: {len(successful)}
└─ Success Rate: {(len(successful) / len(results) * 100):.1f}% if results else 0.0%

💰 FINANCIALS
├─ Revenue: ${total_revenue:.2f}
├─ Costs: ${total_cost:.2f}
├─ Profit: ${total_profit:.2f}
└─ ROI: {(total_profit / total_cost * 100):.1f}% if total_cost > 0 else 'N/A'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return report
    
    def generate_summary_stats(self) -> Dict:
        """
        Generate summary statistics.
        
        Returns:
            Dictionary with key metrics
        """
        # All-time stats
        all_results = self.session.query(PublishResult).all()
        all_content = self.session.query(GeneratedContent).all()
        all_opps = self.session.query(Opportunity).all()
        
        total_revenue = sum(r.actual_revenue for r in all_results)
        total_cost = sum(r.actual_cost for r in all_results)
        
        return {
            'total_opportunities': len(all_opps),
            'total_content_generated': len(all_content),
            'total_published': len(all_results),
            'total_revenue': round(total_revenue, 2),
            'total_cost': round(total_cost, 2),
            'total_profit': round(total_revenue - total_cost, 2),
            'average_profit_per_operation': round(
                (total_revenue - total_cost) / len(all_results), 2
            ) if all_results else 0
        }
    
    def get_top_performing_content_types(self, limit: int = 3) -> list:
        """
        Get top performing content types by profit.
        
        Args:
            limit: Number of top types to return
            
        Returns:
            List of (content_type, avg_profit) tuples
        """
        results = self.session.query(PublishResult).all()
        
        # Group by content type
        type_profits = {}
        type_counts = {}
        
        for result in results:
            content = self.session.query(GeneratedContent).filter_by(
                id=result.content_id
            ).first()
            
            if content:
                ctype = content.content_type
                type_profits[ctype] = type_profits.get(ctype, 0) + result.actual_profit
                type_counts[ctype] = type_counts.get(ctype, 0) + 1
        
        # Calculate averages
        avg_profits = [
            (ctype, type_profits[ctype] / type_counts[ctype])
            for ctype in type_profits
        ]
        
        # Sort and limit
        top = sorted(avg_profits, key=lambda x: x[1], reverse=True)[:limit]
        
        return top

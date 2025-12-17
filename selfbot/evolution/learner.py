"""
Experience learner - learns from successes and failures.
"""
from typing import Dict
from datetime import datetime
from selfbot.database.models import LearningRecord
import logging

logger = logging.getLogger(__name__)


class ExperienceLearner:
    """Learns from operational results to improve future decisions"""
    
    def __init__(self, db_session):
        self.session = db_session
        logger.info("ExperienceLearner initialized")
    
    def record_opportunity_outcome(self, opportunity: Dict, content: Dict, result: Dict):
        """
        Record the outcome of an opportunity.
        
        Args:
            opportunity: Original opportunity
            content: Generated content
            result: Publishing result
        """
        success = result.get('status') in ['accepted', 'earning', 'published']
        profit = result.get('actual_profit', 0.0)
        
        # Extract features that led to this outcome
        features = {
            'content_type': opportunity.get('content_type'),
            'source': opportunity.get('source'),
            'opportunity_score': opportunity.get('opportunity_score'),
            'content_quality': content.get('quality_score'),
            'ai_provider': content.get('metadata', {}).get('ai_provider'),
            'estimated_revenue': opportunity.get('estimated_revenue'),
            'actual_revenue': result.get('actual_revenue')
        }
        
        # Generate insights
        insights = self._generate_insights(success, profit, features)
        
        # Save learning record
        record = LearningRecord(
            opportunity_id=opportunity.get('id'),
            content_id=content.get('id'),
            result_id=result.get('id'),
            action_type='full_cycle',
            success=success,
            profit=profit,
            features=features,
            insights=insights
        )
        
        self.session.add(record)
        self.session.commit()
        
        logger.info(f"Recorded learning: {'SUCCESS' if success else 'FAILURE'} - Profit: ${profit:.2f}")
    
    def _generate_insights(self, success: bool, profit: float, features: Dict) -> str:
        """Generate human-readable insights from outcome"""
        insights = []
        
        if success and profit > 10:
            insights.append(f"High-profit opportunity: {features['content_type']} from {features['source']}")
        
        if not success:
            insights.append(f"Failed: {features['content_type']} - may need better quality or different approach")
        
        if features.get('content_quality', 0) < 0.6 and not success:
            insights.append("Low content quality may have contributed to failure")
        
        if features.get('opportunity_score', 0) < 0.7 and profit < 5:
            insights.append("Low opportunity score correlated with low profit")
        
        return "; ".join(insights) if insights else "Normal outcome"
    
    def get_successful_patterns(self, limit: int = 10) -> list:
        """
        Get patterns from successful operations.
        
        Args:
            limit: Number of successful patterns to return
            
        Returns:
            List of successful learning records
        """
        records = self.session.query(LearningRecord).filter(
            LearningRecord.success == True,
            LearningRecord.profit > 0
        ).order_by(LearningRecord.profit.desc()).limit(limit).all()
        
        return [r.to_dict() for r in records]
    
    def get_failure_patterns(self, limit: int = 10) -> list:
        """
        Get patterns from failed operations.
        
        Args:
            limit: Number of failure patterns to return
            
        Returns:
            List of failed learning records
        """
        records = self.session.query(LearningRecord).filter(
            LearningRecord.success == False
        ).order_by(LearningRecord.created_at.desc()).limit(limit).all()
        
        return [r.to_dict() for r in records]
    
    def analyze_content_type_performance(self) -> Dict:
        """
        Analyze which content types perform best.
        
        Returns:
            Dictionary with content type statistics
        """
        records = self.session.query(LearningRecord).all()
        
        type_stats = {}
        
        for record in records:
            ctype = record.features.get('content_type', 'unknown')
            
            if ctype not in type_stats:
                type_stats[ctype] = {
                    'count': 0,
                    'successes': 0,
                    'total_profit': 0.0
                }
            
            type_stats[ctype]['count'] += 1
            if record.success:
                type_stats[ctype]['successes'] += 1
            type_stats[ctype]['total_profit'] += record.profit
        
        # Calculate success rates and average profits
        for ctype in type_stats:
            stats = type_stats[ctype]
            stats['success_rate'] = stats['successes'] / stats['count'] if stats['count'] > 0 else 0
            stats['avg_profit'] = stats['total_profit'] / stats['count'] if stats['count'] > 0 else 0
        
        return type_stats

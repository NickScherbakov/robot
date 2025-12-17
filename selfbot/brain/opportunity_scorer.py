"""
Opportunity scorer - evaluates and scores opportunities.
"""
from typing import Dict, List
from selfbot.config import SelfBotConfig
import logging

logger = logging.getLogger(__name__)


class OpportunityScorer:
    """Scores opportunities based on profitability and feasibility"""
    
    def __init__(self):
        self.config = SelfBotConfig
        logger.info("OpportunityScorer initialized")
    
    def score_opportunity(self, opportunity: Dict) -> float:
        """
        Score an opportunity from 0 to 1.
        
        Factors:
        - Estimated profit margin
        - Content type feasibility
        - Revenue potential
        - Requirements complexity
        
        Args:
            opportunity: Opportunity dictionary
            
        Returns:
            Score between 0 and 1 (higher is better)
        """
        score = 0.0
        
        # Factor 1: Profit margin (40% weight)
        estimated_revenue = opportunity.get('estimated_revenue', 0)
        estimated_cost = self._estimate_cost(opportunity)
        
        if estimated_revenue > 0:
            profit_margin = (estimated_revenue - estimated_cost) / estimated_revenue
            profit_score = min(profit_margin / 0.9, 1.0)  # Normalize to 0-1
            score += profit_score * 0.4
        
        # Factor 2: Revenue potential (30% weight)
        revenue_score = min(estimated_revenue / 50.0, 1.0)  # Normalize (max $50)
        score += revenue_score * 0.3
        
        # Factor 3: Content type feasibility (20% weight)
        content_type = opportunity.get('content_type', 'unknown')
        feasibility = {
            'article': 0.9,
            'seo_content': 0.95,
            'code': 0.7,
            'image': 0.3  # Not yet implemented
        }.get(content_type, 0.5)
        score += feasibility * 0.2
        
        # Factor 4: Source reliability (10% weight)
        source = opportunity.get('source', 'unknown')
        reliability = {
            'rss': 0.6,
            'rss_demo': 0.8,
            'freelance_demo': 0.9,
            'content_market_demo': 0.85
        }.get(source, 0.5)
        score += reliability * 0.1
        
        return round(score, 3)
    
    def _estimate_cost(self, opportunity: Dict) -> float:
        """Estimate cost of fulfilling opportunity"""
        content_type = opportunity.get('content_type', 'article')
        requirements = opportunity.get('requirements', {})
        word_count = requirements.get('word_count', 800)
        
        # Get economics from config
        economics = self.config.ECONOMICS.get(content_type, {})
        
        # Use middle of cost range
        min_cost = economics.get('ai_cost_min', 0.01)
        max_cost = economics.get('ai_cost_max', 0.10)
        avg_cost = (min_cost + max_cost) / 2
        
        # Adjust based on word count
        if word_count > 1000:
            avg_cost *= 1.5
        
        return round(avg_cost, 4)
    
    def rank_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """
        Rank opportunities by score (highest first).
        
        Args:
            opportunities: List of opportunity dictionaries
            
        Returns:
            Sorted list with scores added
        """
        for opp in opportunities:
            opp['opportunity_score'] = self.score_opportunity(opp)
        
        # Sort by score descending
        ranked = sorted(opportunities, key=lambda x: x['opportunity_score'], reverse=True)
        
        logger.info(f"Ranked {len(ranked)} opportunities")
        return ranked
    
    def filter_by_min_score(self, opportunities: List[Dict], min_score: float = None) -> List[Dict]:
        """
        Filter opportunities by minimum score.
        
        Args:
            opportunities: List of opportunities
            min_score: Minimum score threshold (uses config default if None)
            
        Returns:
            Filtered list
        """
        if min_score is None:
            min_score = self.config.MIN_OPPORTUNITY_SCORE
        
        filtered = [opp for opp in opportunities if opp.get('opportunity_score', 0) >= min_score]
        
        logger.info(f"Filtered to {len(filtered)} opportunities with score >= {min_score}")
        return filtered

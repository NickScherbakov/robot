"""
Decision engine - the brain that makes all decisions.
"""
from typing import List, Dict, Optional
from .opportunity_scorer import OpportunityScorer
from .strategy import EarningStrategy
from selfbot.config import SelfBotConfig
import logging

logger = logging.getLogger(__name__)


class DecisionEngine:
    """Main decision-making engine for SelfBot"""
    
    def __init__(self):
        self.scorer = OpportunityScorer()
        self.strategy = EarningStrategy()
        self.config = SelfBotConfig
        logger.info("DecisionEngine initialized")
    
    def evaluate_and_select(self, opportunities: List[Dict], budget: float) -> List[Dict]:
        """
        Evaluate opportunities and select the best ones.
        
        Args:
            opportunities: List of discovered opportunities
            budget: Available budget for generation
            
        Returns:
            List of selected opportunities with strategies
        """
        if not opportunities:
            logger.info("No opportunities to evaluate")
            return []
        
        logger.info(f"Evaluating {len(opportunities)} opportunities with budget ${budget:.2f}")
        
        # Step 1: Score all opportunities
        scored_opps = self.scorer.rank_opportunities(opportunities)
        
        # Step 2: Filter by minimum score
        filtered_opps = self.scorer.filter_by_min_score(scored_opps)
        
        if not filtered_opps:
            logger.warning("No opportunities passed minimum score threshold")
            return []
        
        # Step 3: Select opportunities that fit budget
        selected = self._select_within_budget(filtered_opps, budget)
        
        # Step 4: Assign strategies to selected opportunities
        for opp in selected:
            opp['strategy'] = self.strategy.get_strategy(opp)
            
            # Optimize AI provider based on budget
            remaining_budget = budget - sum(
                self.scorer._estimate_cost(o) for o in selected[:selected.index(opp)]
            )
            opp['strategy']['ai_provider'] = self.strategy.optimize_provider_selection(
                opp['content_type'],
                remaining_budget
            )
        
        logger.info(f"Selected {len(selected)} opportunities for execution")
        return selected
    
    def _select_within_budget(self, opportunities: List[Dict], budget: float) -> List[Dict]:
        """
        Select opportunities that fit within budget.
        
        Uses greedy algorithm: select highest-scored opportunities
        that fit in budget.
        
        Args:
            opportunities: Scored and ranked opportunities
            budget: Available budget
            
        Returns:
            Selected opportunities
        """
        selected = []
        remaining_budget = budget
        max_opportunities = self.config.MAX_OPPORTUNITIES_PER_CYCLE
        
        for opp in opportunities:
            if len(selected) >= max_opportunities:
                break
            
            estimated_cost = self.scorer._estimate_cost(opp)
            
            if estimated_cost <= remaining_budget:
                selected.append(opp)
                remaining_budget -= estimated_cost
                logger.debug(f"Selected: {opp['title'][:50]}... (cost: ${estimated_cost:.4f})")
            else:
                logger.debug(f"Skipped: {opp['title'][:50]}... (insufficient budget)")
        
        return selected
    
    def should_reinvest(self, current_profit: float, total_earned: float) -> bool:
        """
        Decide whether to reinvest profits.
        
        Args:
            current_profit: Profit from recent cycle
            total_earned: Total earnings so far
            
        Returns:
            True if should reinvest
        """
        if not self.config.AUTO_REINVEST:
            return False
        
        # Only reinvest if we're profitable
        if current_profit > 0:
            logger.info(f"Recommending reinvestment: profit=${current_profit:.2f}")
            return True
        
        return False
    
    def calculate_reinvestment_amount(self, profit: float) -> float:
        """
        Calculate how much to reinvest.
        
        Args:
            profit: Recent profit
            
        Returns:
            Amount to reinvest
        """
        reinvest_percentage = self.config.REINVEST_PERCENTAGE / 100
        amount = profit * reinvest_percentage
        
        logger.info(f"Reinvestment amount: ${amount:.2f} ({self.config.REINVEST_PERCENTAGE}% of ${profit:.2f})")
        return round(amount, 2)
    
    def should_execute_opportunity(self, opportunity: Dict, content_quality: float) -> bool:
        """
        Decide whether to execute (publish) generated content.
        
        Args:
            opportunity: Opportunity dict
            content_quality: Quality score of generated content
            
        Returns:
            True if should publish
        """
        # Don't publish low-quality content
        if content_quality < 0.5:
            logger.warning(f"Content quality too low: {content_quality:.2f}")
            return False
        
        # Check if opportunity still viable
        score = opportunity.get('opportunity_score', 0)
        if score < self.config.MIN_OPPORTUNITY_SCORE:
            logger.warning(f"Opportunity score too low: {score:.2f}")
            return False
        
        # If approval required, don't auto-publish
        if self.config.REQUIRE_APPROVAL:
            logger.info("Approval required before publishing")
            return False
        
        # Auto-publish enabled and quality is good
        if self.config.AUTO_PUBLISH and content_quality >= 0.7:
            logger.info("Auto-publishing approved")
            return True
        
        return False

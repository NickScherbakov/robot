"""
Main entry point for SelfEarnBot.
Runs the autonomous earning cycle.
"""
import time
import logging
from datetime import datetime
from typing import Dict, List

from selfbot.config import SelfBotConfig
from selfbot.database import SelfBotDatabase, Opportunity, GeneratedContent, PublishResult
from selfbot.scanner import RSSScanner, FreelanceScanner, ContentMarketScanner
from selfbot.generator import ArticleGenerator, CodeGenerator
from selfbot.publisher import FreelancePublisher, PlatformPublisher
from selfbot.brain import DecisionEngine
from selfbot.finance import FinanceTracker, AutoReinvestor, SelfBotReports
from selfbot.evolution import ExperienceLearner, StrategyOptimizer
from backend.ai_providers import AIManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class SelfEarnBot:
    """
    Autonomous AI Content Arbitrage Bot.
    
    The bot operates in cycles:
    1. Scan for opportunities
    2. Evaluate and select best opportunities
    3. Generate content using AI
    4. Publish/submit content
    5. Track finances and ROI
    6. Learn from results
    7. Reinvest profits
    """
    
    def __init__(self):
        """Initialize SelfEarnBot"""
        logger.info("🤖 Initializing SelfEarnBot...")
        
        # Validate configuration
        SelfBotConfig.validate()
        
        # Initialize database
        self.db = SelfBotDatabase(SelfBotConfig.DATABASE_PATH).initialize()
        self.session = self.db.get_session()
        
        # Initialize scanners
        self.scanners = [
            RSSScanner(SelfBotConfig.RSS_FEEDS),
            FreelanceScanner(),
            ContentMarketScanner()
        ]
        
        # Initialize AI manager and generators
        self.ai_manager = AIManager()
        self.generators = {
            'article': ArticleGenerator(self.ai_manager),
            'seo_content': ArticleGenerator(self.ai_manager),
            'code': CodeGenerator(self.ai_manager)
        }
        
        # Initialize publishers
        self.publishers = {
            'freelance': FreelancePublisher(),
            'platform': PlatformPublisher()
        }
        
        # Initialize brain
        self.brain = DecisionEngine()
        
        # Initialize finance management
        self.finance_tracker = FinanceTracker(self.session)
        self.finance_tracker.set_budget(SelfBotConfig.INITIAL_BUDGET)
        self.reinvestor = AutoReinvestor(self.finance_tracker)
        self.reports = SelfBotReports(self.session)
        
        # Initialize learning
        self.learner = ExperienceLearner(self.session)
        self.optimizer = StrategyOptimizer(self.learner)
        
        self.running = False
        self.cycle_count = 0
        
        logger.info("✅ SelfEarnBot initialized successfully")
    
    def run_cycle(self) -> Dict:
        """
        Run one complete earning cycle.
        
        Returns:
            Cycle results dictionary
        """
        self.cycle_count += 1
        logger.info(f"\n{'='*50}")
        logger.info(f"🔄 Starting Cycle #{self.cycle_count}")
        logger.info(f"{'='*50}\n")
        
        cycle_start = datetime.utcnow()
        results = {
            'opportunities_found': 0,
            'opportunities_selected': 0,
            'content_generated': 0,
            'content_published': 0,
            'revenue': 0.0,
            'costs': 0.0,
            'profit': 0.0
        }
        
        try:
            # Step 1: Scan for opportunities
            logger.info("📡 Step 1: Scanning for opportunities...")
            opportunities = self._scan_opportunities()
            results['opportunities_found'] = len(opportunities)
            
            if not opportunities:
                logger.info("No opportunities found this cycle")
                return results
            
            # Step 2: Evaluate and select best opportunities
            logger.info("\n🧠 Step 2: Evaluating opportunities...")
            selected_opps = self.brain.evaluate_and_select(
                opportunities,
                self.finance_tracker.get_budget()
            )
            results['opportunities_selected'] = len(selected_opps)
            
            if not selected_opps:
                logger.info("No opportunities selected (budget or score constraints)")
                return results
            
            # Step 3-6: Process each selected opportunity
            for opp in selected_opps:
                opp_result = self._process_opportunity(opp)
                
                if opp_result['generated']:
                    results['content_generated'] += 1
                if opp_result['published']:
                    results['content_published'] += 1
                
                results['revenue'] += opp_result['revenue']
                results['costs'] += opp_result['costs']
            
            results['profit'] = results['revenue'] - results['costs']
            
            # Step 7: Reinvest profits
            if results['profit'] > 0:
                logger.info(f"\n💰 Step 7: Reinvesting profits...")
                reinvested = self.reinvestor.execute_reinvestment(results['profit'])
                results['reinvested'] = reinvested
            
            # Generate cycle report
            logger.info("\n" + self.reports.generate_cycle_report())
            
        except Exception as e:
            logger.error(f"Error in cycle: {e}", exc_info=True)
        
        cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
        logger.info(f"\n✅ Cycle #{self.cycle_count} completed in {cycle_duration:.1f}s")
        logger.info(f"Profit this cycle: ${results['profit']:.2f}")
        
        return results
    
    def _scan_opportunities(self) -> List[Dict]:
        """Scan all sources for opportunities"""
        all_opportunities = []
        
        for scanner in self.scanners:
            if scanner.is_enabled():
                try:
                    opps = scanner.scan()
                    all_opportunities.extend(opps)
                    logger.info(f"  {scanner.name}: found {len(opps)} opportunities")
                except Exception as e:
                    logger.error(f"Error in {scanner.name}: {e}")
        
        # Save to database
        for opp_data in all_opportunities:
            opp = Opportunity(
                source=opp_data['source'],
                source_url=opp_data.get('source_url'),
                title=opp_data['title'],
                description=opp_data['description'],
                content_type=opp_data['content_type'],
                estimated_revenue=opp_data.get('estimated_revenue', 0),
                requirements=opp_data.get('requirements', {})
            )
            self.session.add(opp)
        
        self.session.commit()
        
        return all_opportunities
    
    def _process_opportunity(self, opportunity: Dict) -> Dict:
        """Process a single opportunity through generation and publishing"""
        result = {
            'generated': False,
            'published': False,
            'revenue': 0.0,
            'costs': 0.0
        }
        
        try:
            # Step 3: Generate content
            logger.info(f"\n✍️ Generating: {opportunity['title'][:60]}...")
            
            content_type = opportunity['content_type']
            generator = self.generators.get(content_type)
            
            if not generator:
                logger.warning(f"No generator for type: {content_type}")
                return result
            
            strategy = opportunity.get('strategy', {})
            gen_params = strategy.get('generation_params', {})
            gen_params.update({
                'title': opportunity['title'],
                'ai_provider': strategy.get('ai_provider', 'mistral')
            })
            gen_params['keywords'] = opportunity.get('requirements', {}).get('keywords', [])
            
            content_result = generator.generate(gen_params)
            result['costs'] += content_result['cost']
            self.finance_tracker.record_generation_cost(0, content_result['cost'])
            
            # Save generated content
            content = GeneratedContent(
                content_type=content_type,
                title=content_result['title'],
                content=content_result['content'],
                ai_provider=content_result['metadata'].get('ai_provider', 'unknown'),
                tokens_used=content_result['tokens_used'],
                generation_cost=content_result['cost'],
                quality_score=content_result['quality_score'],
                status='generated'
            )
            self.session.add(content)
            self.session.commit()
            
            result['generated'] = True
            logger.info(f"  ✅ Generated ({content_result['tokens_used']} tokens, ${content_result['cost']:.4f})")
            logger.info(f"  Quality score: {content_result['quality_score']:.2f}")
            
            # Step 4: Decide whether to publish
            should_publish = self.brain.should_execute_opportunity(
                opportunity,
                content_result['quality_score']
            )
            
            if not should_publish and SelfBotConfig.REQUIRE_APPROVAL:
                logger.info("  ⏸️  Requires manual approval before publishing")
                content.status = 'pending_approval'
                self.session.commit()
                return result
            
            # Step 5: Publish content
            logger.info("  📤 Publishing...")
            
            publisher_type = strategy.get('publisher', 'platform')
            publisher = self.publishers.get(publisher_type)
            
            if not publisher:
                logger.warning(f"No publisher for type: {publisher_type}")
                return result
            
            publish_result = publisher.publish(content_result, opportunity)
            
            # Step 6: Track results
            pub_record = PublishResult(
                content_id=content.id,
                platform=publisher_type,
                platform_url=publish_result.get('platform_url'),
                status=publish_result['status'],
                actual_revenue=publish_result.get('estimated_revenue', 0),
                actual_cost=content_result['cost'],
                actual_profit=publish_result.get('estimated_revenue', 0) - content_result['cost'],
                published_at=datetime.utcnow()
            )
            
            if publish_result['status'] in ['published', 'submitted']:
                pub_record.roi = self.finance_tracker.calculate_roi(
                    pub_record.actual_cost,
                    pub_record.actual_revenue
                )
            
            self.session.add(pub_record)
            self.session.commit()
            
            result['published'] = True
            result['revenue'] = pub_record.actual_revenue
            
            if pub_record.actual_revenue > 0:
                self.finance_tracker.record_revenue(pub_record.id, pub_record.actual_revenue)
            
            logger.info(f"  ✅ {publish_result['status']}: ${pub_record.actual_revenue:.2f} revenue")
            logger.info(f"  💰 Profit: ${pub_record.actual_profit:.2f} (ROI: {pub_record.roi*100:.1f}%)")
            
            # Learn from this result
            self.learner.record_opportunity_outcome(
                opportunity,
                content_result,
                publish_result
            )
            
        except Exception as e:
            logger.error(f"Error processing opportunity: {e}", exc_info=True)
        
        return result
    
    def run(self, max_cycles: int = None, interval: int = None):
        """
        Run the bot continuously.
        
        Args:
            max_cycles: Maximum number of cycles (None = infinite)
            interval: Seconds between cycles (None = use config)
        """
        if interval is None:
            interval = SelfBotConfig.SCAN_INTERVAL
        
        self.running = True
        logger.info(f"\n{'='*50}")
        logger.info("🚀 SelfEarnBot Starting Autonomous Operation")
        logger.info(f"{'='*50}")
        logger.info(f"Initial budget: ${SelfBotConfig.INITIAL_BUDGET:.2f}")
        logger.info(f"Cycle interval: {interval}s")
        logger.info(f"Max cycles: {max_cycles or 'Unlimited'}")
        logger.info(f"{'='*50}\n")
        
        try:
            while self.running:
                # Run a cycle
                self.run_cycle()
                
                # Check if we've hit max cycles
                if max_cycles and self.cycle_count >= max_cycles:
                    logger.info(f"\n✅ Reached maximum cycles ({max_cycles})")
                    break
                
                # Wait before next cycle
                logger.info(f"\n⏳ Waiting {interval}s until next cycle...\n")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Stopping SelfEarnBot (user interrupt)")
        except Exception as e:
            logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Stop the bot and cleanup"""
        self.running = False
        
        # Final report
        logger.info("\n" + "="*50)
        logger.info("📊 FINAL REPORT")
        logger.info("="*50)
        
        summary = self.reports.generate_summary_stats()
        for key, value in summary.items():
            logger.info(f"{key}: {value}")
        
        logger.info("\n" + self.optimizer.get_optimization_report())
        
        # Cleanup
        self.session.close()
        self.db.close()
        
        logger.info("👋 SelfEarnBot stopped")


def main():
    """Main entry point"""
    bot = SelfEarnBot()
    
    # Run for demonstration (3 cycles, 60s interval)
    # In production, remove max_cycles for infinite operation
    bot.run(max_cycles=3, interval=60)


if __name__ == '__main__':
    main()

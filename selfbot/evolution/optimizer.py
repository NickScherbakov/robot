"""
Strategy optimizer - optimizes strategies based on learning.
"""
from typing import Dict
from selfbot.config import SelfBotConfig
import logging

logger = logging.getLogger(__name__)


class StrategyOptimizer:
    """Optimizes earning strategies based on historical performance"""
    
    def __init__(self, learner):
        self.learner = learner
        self.config = SelfBotConfig
        logger.info("StrategyOptimizer initialized")
    
    def optimize_opportunity_selection(self) -> Dict:
        """
        Optimize opportunity selection criteria based on learning.
        
        Returns:
            Optimized selection parameters
        """
        # Analyze content type performance
        type_performance = self.learner.analyze_content_type_performance()
        
        # Find best performing type
        best_type = None
        best_avg_profit = 0
        
        for ctype, stats in type_performance.items():
            if stats['avg_profit'] > best_avg_profit and stats['success_rate'] > 0.5:
                best_type = ctype
                best_avg_profit = stats['avg_profit']
        
        # Get successful patterns
        successful_patterns = self.learner.get_successful_patterns(limit=20)
        
        # Calculate average opportunity score of successful operations
        if successful_patterns:
            avg_successful_score = sum(
                p['features'].get('opportunity_score', 0) for p in successful_patterns
            ) / len(successful_patterns)
        else:
            avg_successful_score = self.config.MIN_OPPORTUNITY_SCORE
        
        recommendations = {
            'preferred_content_type': best_type,
            'min_opportunity_score': max(avg_successful_score - 0.1, 0.5),
            'focus_areas': [],
            'avoid_areas': []
        }
        
        # Add recommendations based on performance
        for ctype, stats in type_performance.items():
            if stats['success_rate'] > 0.7:
                recommendations['focus_areas'].append(ctype)
            elif stats['success_rate'] < 0.3:
                recommendations['avoid_areas'].append(ctype)
        
        logger.info(f"Optimized selection: prefer {best_type}, min score {recommendations['min_opportunity_score']:.2f}")
        return recommendations
    
    def optimize_ai_provider_selection(self) -> Dict:
        """
        Optimize AI provider selection based on cost/quality.
        
        Returns:
            Provider recommendations by content type
        """
        successful_patterns = self.learner.get_successful_patterns(limit=50)
        
        # Group by content type and provider
        provider_performance = {}
        
        for pattern in successful_patterns:
            features = pattern.get('features', {})
            ctype = features.get('content_type', 'unknown')
            provider = features.get('ai_provider', 'unknown')
            profit = pattern.get('profit', 0)
            
            # Use tuple as key to avoid string parsing issues
            key = (ctype, provider)
            if key not in provider_performance:
                provider_performance[key] = {
                    'count': 0,
                    'total_profit': 0
                }
            
            provider_performance[key]['count'] += 1
            provider_performance[key]['total_profit'] += profit
        
        # Calculate averages and make recommendations
        recommendations = {}
        
        for (ctype, provider), stats in provider_performance.items():
            if stats['count'] > 2:  # Need at least 3 samples
                avg_profit = stats['total_profit'] / stats['count']
                
                if ctype not in recommendations or avg_profit > recommendations[ctype]['avg_profit']:
                    recommendations[ctype] = {
                        'provider': provider,
                        'avg_profit': avg_profit
                    }
        
        return recommendations
    
    def suggest_improvements(self) -> list:
        """
        Generate improvement suggestions based on learning.
        
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        # Analyze failures
        failures = self.learner.get_failure_patterns(limit=10)
        
        if len(failures) > 5:
            common_fail_type = max(
                set(f['features'].get('content_type', 'unknown') for f in failures),
                key=lambda t: sum(1 for f in failures if f['features'].get('content_type') == t)
            )
            suggestions.append(f"Consider avoiding {common_fail_type} - high failure rate")
        
        # Analyze content type performance
        type_perf = self.learner.analyze_content_type_performance()
        
        for ctype, stats in type_perf.items():
            if stats['success_rate'] > 0.8 and stats['count'] > 3:
                suggestions.append(f"Focus more on {ctype} - {stats['success_rate']:.0%} success rate")
        
        # Check if we have enough data
        total_records = sum(stats['count'] for stats in type_perf.values())
        if total_records < 10:
            suggestions.append("Need more data for reliable optimization (< 10 operations)")
        
        return suggestions
    
    def get_optimization_report(self) -> str:
        """
        Generate a full optimization report.
        
        Returns:
            Formatted report string
        """
        selection_opts = self.optimize_opportunity_selection()
        provider_opts = self.optimize_ai_provider_selection()
        suggestions = self.suggest_improvements()
        
        report = f"""
🧠 STRATEGY OPTIMIZATION REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 OPPORTUNITY SELECTION
├─ Preferred Type: {selection_opts.get('preferred_content_type', 'N/A')}
├─ Min Score: {selection_opts.get('min_opportunity_score', 0):.2f}
├─ Focus On: {', '.join(selection_opts.get('focus_areas', [])) or 'All types'}
└─ Avoid: {', '.join(selection_opts.get('avoid_areas', [])) or 'None'}

🤖 AI PROVIDER RECOMMENDATIONS
"""
        
        for ctype, rec in provider_opts.items():
            report += f"├─ {ctype}: {rec['provider']} (avg profit: ${rec['avg_profit']:.2f})\n"
        
        report += "\n💡 IMPROVEMENT SUGGESTIONS\n"
        for i, suggestion in enumerate(suggestions, 1):
            report += f"{i}. {suggestion}\n"
        
        report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return report

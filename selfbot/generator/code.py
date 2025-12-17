"""
Code generator using AI APIs.
Generates scripts, code snippets, and programs.
"""
from .base import BaseGenerator
from typing import Dict
from backend.ai_providers import AIManager
import logging

logger = logging.getLogger(__name__)


class CodeGenerator(BaseGenerator):
    """Generates code and scripts"""
    
    def __init__(self, ai_manager: AIManager = None):
        super().__init__("CodeGenerator")
        self.ai_manager = ai_manager or AIManager()
    
    def generate(self, requirements: Dict) -> Dict:
        """
        Generate code based on requirements.
        
        Args:
            requirements: Dict with keys:
                - title or description: What the code should do
                - language: Programming language (default: python)
                - keywords: Related concepts/libraries
                - ai_provider: AI provider to use (default: openai for code)
                
        Returns:
            Generated code data
        """
        if not self.validate_requirements(requirements):
            raise ValueError("Invalid requirements for code generation")
        
        # Extract requirements
        description = requirements.get('title') or requirements.get('description', 'Code script')
        language = requirements.get('language', 'python').lower()
        keywords = requirements.get('keywords', [])
        ai_provider = requirements.get('ai_provider', 'openai')  # OpenAI generally better for code
        
        # Build prompt
        prompt = self._build_code_prompt(description, language, keywords)
        
        logger.info(f"Generating {language} code: '{description}'")
        
        try:
            # Generate using AI
            result = self.ai_manager.execute_task(
                prompt=prompt,
                provider=ai_provider,
                max_tokens=1500
            )
            
            # Extract code from response
            code = self._extract_code(result['response'])
            
            # Assess quality
            quality_score = self._assess_code_quality(code, language)
            
            return {
                'content': code,
                'title': description,
                'tokens_used': result['tokens_used'],
                'cost': result['cost'],
                'quality_score': quality_score,
                'metadata': {
                    'ai_provider': ai_provider,
                    'language': language,
                    'lines_of_code': len(code.split('\n'))
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            raise
    
    def _build_code_prompt(self, description: str, language: str, keywords: list) -> str:
        """Build prompt for code generation"""
        keywords_str = ', '.join(keywords[:3]) if keywords else ''
        
        prompt = f"""Write a {language} script that: {description}

Requirements:
- Use clean, well-commented code
- Follow {language} best practices
- Include error handling where appropriate
"""
        
        if keywords_str:
            prompt += f"- Use these concepts/libraries if relevant: {keywords_str}\n"
        
        prompt += f"\nProvide only the {language} code with comments:\n\n```{language}\n"
        
        return prompt
    
    def _extract_code(self, response: str) -> str:
        """Extract code from AI response (remove markdown formatting)"""
        # Remove markdown code blocks if present
        lines = response.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                code_lines.append(line)
        
        # If code block markers were found, return extracted code
        if code_lines:
            return '\n'.join(code_lines).strip()
        
        # Otherwise, return response as-is
        return response
    
    def _assess_code_quality(self, code: str, language: str) -> float:
        """
        Self-assess code quality.
        
        Returns:
            Quality score between 0 and 1
        """
        score = 0.5  # Base score
        
        # Check code length
        lines = code.split('\n')
        if len(lines) > 10:
            score += 0.2
        
        # Check for comments
        comment_markers = {
            'python': '#',
            'javascript': '//',
            'java': '//',
            'c': '//',
            'cpp': '//'
        }
        marker = comment_markers.get(language, '#')
        has_comments = any(marker in line for line in lines)
        if has_comments:
            score += 0.2
        
        # Check for basic structure (functions/classes)
        structure_keywords = ['def ', 'function ', 'class ', 'func ']
        has_structure = any(kw in code for kw in structure_keywords)
        if has_structure:
            score += 0.1
        
        return min(score, 1.0)
    
    def estimate_cost(self, requirements: Dict) -> float:
        """Estimate cost for code generation"""
        ai_provider = requirements.get('ai_provider', 'openai')
        
        # Code typically requires more tokens
        estimated_tokens = 1000
        
        # Cost per 1K tokens
        cost_rates = {
            'mistral': 0.0002,
            'openai': 0.002
        }
        
        cost_per_1k = cost_rates.get(ai_provider, 0.002)
        estimated_cost = (estimated_tokens / 1000) * cost_per_1k
        
        return round(estimated_cost, 4)

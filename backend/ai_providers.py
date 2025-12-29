"""
AI provider integrations for the Earning Robot.
Supports OpenAI and Mistral AI APIs.
"""
import openai
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from backend.config import Config
import logging

logger = logging.getLogger(__name__)


class AIProvider:
    """Base AI provider class"""
    
    def __init__(self):
        self.name = "base"
    
    def generate_response(self, prompt, max_tokens=500):
        """Generate AI response - to be implemented by subclasses"""
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI API integration"""
    
    def __init__(self):
        super().__init__()
        self.name = "openai"
        if Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY
        else:
            logger.warning("OpenAI API key not configured")
    
    def generate_response(self, prompt, max_tokens=500, model="gpt-4o-mini"):
        """
        Generate response using OpenAI API
        
        Args:
            prompt: User's input prompt
            max_tokens: Maximum tokens in response
            model: OpenAI model to use
            
        Returns:
            dict with 'response', 'tokens_used', and 'cost'
        """
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            
            tokens_used = response.usage.total_tokens
            # Approximate cost calculation (2025 models)
            price_per_1k = {
                'gpt-4o-mini': 0.0015,
                'gpt-4o': 0.01,
                'gpt-3.5-turbo': 0.002,
            }.get(model, 0.002)
            cost = (tokens_used / 1000) * price_per_1k
            
            return {
                'response': response.choices[0].message.content,
                'tokens_used': tokens_used,
                'cost': cost,
                'model': model
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class MistralProvider(AIProvider):
    """Mistral AI integration"""
    
    def __init__(self):
        super().__init__()
        self.name = "mistral"
        if Config.MISTRAL_API_KEY:
            self.client = MistralClient(api_key=Config.MISTRAL_API_KEY)
        else:
            self.client = None
            logger.warning("Mistral API key not configured")
    
    def generate_response(self, prompt, max_tokens=500, model="mistral-tiny"):
        """
        Generate response using Mistral AI
        
        Args:
            prompt: User's input prompt
            max_tokens: Maximum tokens in response
            model: Mistral model to use (mistral-tiny, mistral-small, mistral-medium)
            
        Returns:
            dict with 'response', 'tokens_used', and 'cost'
        """
        if not self.client:
            raise ValueError("Mistral API key not configured")
        
        try:
            messages = [ChatMessage(role="user", content=prompt)]
            
            response = self.client.chat(
                model=model,
                messages=messages,
                max_tokens=max_tokens
            )
            
            tokens_used = response.usage.total_tokens
            # Approximate cost calculation (Mistral-tiny: $0.0002 per 1K tokens)
            cost_per_1k = {
                'mistral-tiny': 0.0002,
                'mistral-small': 0.0006,
                'mistral-medium': 0.0027
            }.get(model, 0.0002)
            
            cost = (tokens_used / 1000) * cost_per_1k
            
            return {
                'response': response.choices[0].message.content,
                'tokens_used': tokens_used,
                'cost': cost,
                'model': model
            }
        except Exception as e:
            logger.error(f"Mistral API error: {e}")
            raise


class AIManager:
    """Manages multiple AI providers"""
    
    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider(),
            'mistral': MistralProvider()
        }
    
    def get_provider(self, provider_name='openai'):
        """Get AI provider by name"""
        return self.providers.get(provider_name)
    
    def execute_task(self, prompt, provider='openai', max_tokens=500):
        """
        Execute AI task with specified provider
        
        Args:
            prompt: User's input
            provider: AI provider name
            max_tokens: Maximum response tokens
            
        Returns:
            Response dictionary with results
        """
        ai_provider = self.get_provider(provider)
        if not ai_provider:
            raise ValueError(f"Unknown AI provider: {provider}")
        
        return ai_provider.generate_response(prompt, max_tokens)

"""LLM service with Google Gemini API"""
from typing import List, Dict, Any, Optional
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings


class LLMService:
    """Service for LLM interactions with token counting and cost estimation"""
    
    def __init__(self):
        # Configure Gemini API with new SDK
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL
        self.temperature = settings.GEMINI_TEMPERATURE
        self.max_tokens = settings.GEMINI_MAX_TOKENS
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using Gemini's token counter"""
        try:
            # Use the new SDK's count_tokens method
            result = self.client.models.count_tokens(
                model=self.model_name,
                contents=text
            )
            return result.total_tokens
        except Exception:
            # Fallback: rough estimate (1 token ≈ 4 chars)
            return len(text) // 4
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost based on token usage
        Note: Gemini free tier has no cost, but we track for monitoring
        """
        # Gemini 2.0 Flash pricing (if exceeding free tier):
        # Input: $0.075 per 1M tokens, Output: $0.30 per 1M tokens
        input_cost = (input_tokens / 1_000_000) * 0.075
        output_cost = (output_tokens / 1_000_000) * 0.30
        return input_cost + output_cost
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get chat completion from Gemini
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional parameters for Gemini API
        
        Returns:
            Dict with 'content', 'input_tokens', 'output_tokens', 'total_tokens', 'cost'
        """
        # Convert OpenAI-style messages to Gemini format
        gemini_content = self._convert_messages_to_gemini(messages)
        
        # Prepare generation config
        config = {
            "temperature": temperature or self.temperature,
            "max_output_tokens": max_tokens or self.max_tokens,
        }
        
        # Generate content using new SDK
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=gemini_content,
            config=config
        )
        
        # Extract response content
        content = response.text
        
        # Get token usage
        try:
            if hasattr(response, 'usage_metadata'):
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count
                total_tokens = response.usage_metadata.total_token_count
            else:
                # Fallback if usage metadata not available
                input_tokens = self.count_tokens(str(gemini_content))
                output_tokens = self.count_tokens(content)
                total_tokens = input_tokens + output_tokens
        except AttributeError:
            # Fallback if usage metadata not available
            input_tokens = self.count_tokens(str(gemini_content))
            output_tokens = self.count_tokens(content)
            total_tokens = input_tokens + output_tokens
        
        cost = self.estimate_cost(input_tokens, output_tokens)
        
        return {
            "content": content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost": cost,
            "finish_reason": "stop"
        }
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Get streaming chat completion from Gemini
        
        Yields content chunks
        """
        # Convert OpenAI-style messages to Gemini format
        gemini_content = self._convert_messages_to_gemini(messages)
        
        # Prepare generation config
        config = {
            "temperature": temperature or self.temperature,
            "max_output_tokens": max_tokens or self.max_tokens,
        }
        
        # Generate content with streaming using new SDK
        stream = self.client.aio.models.generate_content_stream(
            model=self.model_name,
            contents=gemini_content,
            config=config
        )
        
        async for chunk in stream:
            if chunk.text:
                yield chunk.text
    
    def _convert_messages_to_gemini(self, messages: List[Dict[str, str]]) -> str:
        """
        Convert OpenAI-style messages to Gemini format
        
        For the new SDK, we'll combine messages into a single prompt string
        """
        prompt_parts = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)


# Global LLM service instance
llm_service = LLMService()

"""Embedding service with Google Gemini API"""
from typing import List
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings


class EmbeddingService:
    """Service for generating embeddings using Gemini"""
    
    def __init__(self):
        # Configure Gemini API with new SDK
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_EMBEDDING_MODEL
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
        
        Returns:
            List of floats representing the embedding vector
        """
        response = await self.client.aio.models.embed_content(
            model=self.model,
            contents=text
        )
        # The response structure is response.embeddings[0].values
        return list(response.embeddings[0].values)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query
        
        Args:
            query: Query text to embed
        
        Returns:
            List of floats representing the embedding vector
        """
        response = await self.client.aio.models.embed_content(
            model=self.model,
            content=query
        )
        return list(response.embeddings[0].values)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        # Process in batches to avoid rate limits
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Embed each text in the batch
            for text in batch:
                response = await self.client.aio.models.embed_content(
                    model=self.model,
                    contents=text
                )
                embeddings.append(list(response.embeddings[0].values))
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors
        
        Returns:
            Embedding dimension (768 for text-embedding-004)
        """
        # text-embedding-004 produces 768-dimensional embeddings
        return 768


# Global embedding service instance
embedding_service = EmbeddingService()

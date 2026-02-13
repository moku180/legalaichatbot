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
        self.request_count = 0
    
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
        self.request_count += 1
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
            contents=query
        )
        self.request_count += 1
        return list(response.embeddings[0].values)
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with adaptive batching
        
        Uses a fallback strategy:
        1. Try batch of 100
        2. If fails, try batches of 10
        3. If fails, try parallel batches of 5
        4. If fails, sequential processing
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        import asyncio
        import logging
        import time
        
        
        logger = logging.getLogger(__name__)
        total_texts = len(texts)
        logger.info(f"Starting embedding for {total_texts} chunks")
        start_time = time.time()
        initial_request_count = self.request_count
        
        embeddings = []
        
        # Try different batch sizes with adaptive fallback
        # Try different batch sizes with adaptive fallback
        # Reduced max batch size to 5 to prevent OOM on small instances
        batch_sizes = [5, 2, 1]
        
        i = 0
        while i < total_texts:
            batch_processed = False
            
            for batch_size in batch_sizes:
                if batch_processed:
                    break
                    
                batch_end = min(i + batch_size, total_texts)
                batch = texts[i:batch_end]
                
                try:
                    if batch_size == 1:
                        # Sequential processing (last resort)
                        logger.debug(f"Processing chunk {i+1}/{total_texts} sequentially")
                        response = await self._embed_single_with_retry(batch[0])
                        embeddings.append(response)
                        batch_processed = True
                    elif batch_size == 2:
                        # Parallel processing of small batches
                        logger.info(f"Processing chunks {i+1}-{batch_end}/{total_texts} in parallel (batch size: {batch_size})")
                        batch_embeddings = await self._embed_parallel(batch)
                        embeddings.extend(batch_embeddings)
                        batch_processed = True
                    else:
                        # Try larger batch
                        logger.info(f"Processing chunks {i+1}-{batch_end}/{total_texts} (batch size: {batch_size})")
                        response = await self.client.aio.models.embed_content(
                            model=self.model,
                            contents=batch
                        )
                        self.request_count += 1
                        
                        if hasattr(response, 'embeddings'):
                            for emb in response.embeddings:
                                embeddings.append(list(emb.values))
                            batch_processed = True
                            logger.debug(f"Successfully embedded batch of {len(batch)} chunks")
                
                except Exception as e:
                    logger.warning(f"Batch size {batch_size} failed: {str(e)[:100]}")
                    # Try next smaller batch size
                    continue
            
            if not batch_processed:
                logger.error(f"Failed to embed chunk {i+1} after all retry strategies")
                # Skip this chunk to avoid infinite loop
                i += 1
                continue
            
            # Move to next batch
            i = batch_end
            
            # Rate limiting for Gemini Free Tier (15 RPM)
            # Sleep 4 seconds to ensure we don't exceed limit
            # 60s / 15 reqs = 4s per request
            await asyncio.sleep(4)
            
            # Log progress every 50 chunks
            if len(embeddings) % 50 == 0 and len(embeddings) > 0:
                elapsed = time.time() - start_time
                rate = len(embeddings) / elapsed
                eta = (total_texts - len(embeddings)) / rate if rate > 0 else 0
                logger.info(f"Progress: {len(embeddings)}/{total_texts} chunks embedded ({elapsed:.1f}s elapsed, ETA: {eta:.1f}s)")
        
        elapsed = time.time() - start_time
        requests_made = self.request_count - initial_request_count
        logger.info(f"Completed embedding {len(embeddings)}/{total_texts} chunks in {elapsed:.1f}s")
        logger.info(f"Total API Requests used: {requests_made}")
        
        return embeddings
    
    async def _embed_single_with_retry(self, text: str, max_retries: int = 3) -> List[float]:
        """Embed a single text with retry logic"""
        import asyncio
        import logging
        logger = logging.getLogger(__name__)
        
        for attempt in range(max_retries):
            try:
                response = await self.client.aio.models.embed_content(
                    model=self.model,
                    contents=text
                )
                self.request_count += 1
                return list(response.embeddings[0].values)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to embed chunk after {max_retries} attempts: {e}")
                    raise
                logger.warning(f"Retry {attempt + 1}/{max_retries} for single embedding: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _embed_parallel(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts in parallel"""
        import asyncio
        
        tasks = [self._embed_single_with_retry(text) for text in texts]
        return await asyncio.gather(*tasks)
    
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

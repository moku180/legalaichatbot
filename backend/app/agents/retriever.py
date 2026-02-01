"""Retriever Agent - Performs vector search with metadata filtering"""
from typing import List, Dict, Any, Optional
from app.rag.vector_store import vector_store
from app.core.config import settings


class RetrieverAgent:
    """Agent for retrieving relevant document chunks"""
    
    def __init__(self):
        self.top_k = settings.RETRIEVAL_TOP_K
    
    async def retrieve(
        self,
        organization_id: int,
        query: str,
        jurisdiction: Optional[str] = None,
        document_type: Optional[str] = None,
        court_level: Optional[str] = None,
        year: Optional[int] = None,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks with metadata filtering
        
        Args:
            organization_id: Organization ID for tenant isolation
            query: Search query
            jurisdiction: Filter by jurisdiction
            document_type: Filter by document type
            court_level: Filter by court level
            year: Filter by year
            top_k: Number of results
        
        Returns:
            List of retrieved chunks with metadata and scores
        """
        # Build filters
        filters = {}
        if jurisdiction:
            filters["jurisdiction"] = jurisdiction
        if document_type:
            filters["document_type"] = document_type
        if court_level:
            filters["court_level"] = court_level
        if year:
            filters["year"] = year
        
        # Perform search
        results = await vector_store.search(
            organization_id=organization_id,
            query=query,
            top_k=top_k or self.top_k,
            filters=filters if filters else None
        )
        
        # Enrich results with actual text
        # Note: In production, store text separately and join here
        # For now, metadata should contain the text
        enriched_results = []
        for result in results:
            # Get document text from metadata
            # In a real system, you'd fetch from document storage
            enriched_results.append({
                "text": result["metadata"].get("text", ""),
                "metadata": result["metadata"],
                "relevance_score": 1.0 / (1.0 + result["score"])  # Convert distance to similarity
            })
        
        return enriched_results
    
    async def retrieve_with_mmr(
        self,
        organization_id: int,
        query: str,
        diversity_score: float = settings.MMR_DIVERSITY_SCORE,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve with Maximal Marginal Relevance for diversity
        
        MMR balances relevance and diversity to avoid redundant results
        
        Args:
            organization_id: Organization ID
            query: Search query
            diversity_score: Lambda parameter (0=relevance only, 1=diversity only)
            **kwargs: Additional filters
        
        Returns:
            Diverse set of retrieved chunks
        """
        # For simplicity, retrieve more results and apply MMR
        initial_k = (kwargs.get("top_k") or self.top_k) * 2
        
        results = await self.retrieve(
            organization_id=organization_id,
            query=query,
            top_k=initial_k,
            **{k: v for k, v in kwargs.items() if k != "top_k"}
        )
        
        if not results:
            return []
        
        # Simple MMR implementation
        # In production, use proper vector-based MMR
        selected = [results[0]]  # Start with most relevant
        remaining = results[1:]
        
        target_k = kwargs.get("top_k") or self.top_k
        
        while len(selected) < target_k and remaining:
            # Find result that maximizes: relevance - diversity_score * max_similarity_to_selected
            best_idx = 0
            best_score = -float('inf')
            
            for i, candidate in enumerate(remaining):
                relevance = candidate["relevance_score"]
                
                # Simple text-based diversity (in production, use embeddings)
                max_similarity = max([
                    self._text_similarity(candidate["text"], sel["text"])
                    for sel in selected
                ])
                
                mmr_score = relevance - diversity_score * max_similarity
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = i
            
            selected.append(remaining.pop(best_idx))
        
        return selected[:target_k]
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity (Jaccard)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)


# Global retriever agent instance
retriever_agent = RetrieverAgent()

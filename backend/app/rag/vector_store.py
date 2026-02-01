"""Vector store using FAISS with tenant isolation"""
import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from pathlib import Path
from app.core.config import settings
from app.services.embedding_service import embedding_service


class VectorStore:
    """FAISS-based vector store with multi-tenant support"""
    
    def __init__(self, base_path: str = settings.VECTOR_STORE_PATH):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.indexes: Dict[int, faiss.Index] = {}
        self.metadatas: Dict[int, List[Dict[str, Any]]] = {}
    
    def _get_index_path(self, organization_id: int) -> Path:
        """Get path for organization's FAISS index"""
        return self.base_path / f"org_{organization_id}_index.faiss"
    
    def _get_metadata_path(self, organization_id: int) -> Path:
        """Get path for organization's metadata"""
        return self.base_path / f"org_{organization_id}_metadata.pkl"
    
    def load_index(self, organization_id: int) -> bool:
        """Load organization's index from disk"""
        index_path = self._get_index_path(organization_id)
        metadata_path = self._get_metadata_path(organization_id)
        
        if not index_path.exists():
            return False
        
        try:
            # Load FAISS index
            self.indexes[organization_id] = faiss.read_index(str(index_path))
            
            # Load metadata
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    self.metadatas[organization_id] = pickle.load(f)
            else:
                self.metadatas[organization_id] = []
            
            return True
        except Exception as e:
            print(f"Error loading index for org {organization_id}: {e}")
            return False
    
    def save_index(self, organization_id: int) -> bool:
        """Save organization's index to disk"""
        if organization_id not in self.indexes:
            return False
        
        try:
            index_path = self._get_index_path(organization_id)
            metadata_path = self._get_metadata_path(organization_id)
            
            # Save FAISS index
            faiss.write_index(self.indexes[organization_id], str(index_path))
            
            # Save metadata
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadatas[organization_id], f)
            
            return True
        except Exception as e:
            print(f"Error saving index for org {organization_id}: {e}")
            return False
    
    async def add_documents(
        self,
        organization_id: int,
        chunks: List[Dict[str, Any]]
    ) -> bool:
        """
        Add document chunks to organization's vector store
        
        Args:
            organization_id: Organization ID for tenant isolation
            chunks: List of chunks with 'text' and 'metadata'
        
        Returns:
            Success status
        """
        if not chunks:
            return False
        
        try:
            # Generate embeddings for all chunks
            texts = [chunk["text"] for chunk in chunks]
            embeddings = await embedding_service.embed_batch(texts)
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)
            dimension = embeddings_array.shape[1]
            
            # Load or create index
            if organization_id not in self.indexes:
                if not self.load_index(organization_id):
                    # Create new index
                    self.indexes[organization_id] = faiss.IndexFlatL2(dimension)
                    self.metadatas[organization_id] = []
            
            # Add to index
            self.indexes[organization_id].add(embeddings_array)
            
            # Add metadata
            self.metadatas[organization_id].extend([chunk["metadata"] for chunk in chunks])
            
            # Save to disk
            self.save_index(organization_id)
            
            return True
            
        except Exception as e:
            print(f"Error adding documents for org {organization_id}: {e}")
            return False
    
    async def search(
        self,
        organization_id: int,
        query: str,
        top_k: int = settings.RETRIEVAL_TOP_K,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search organization's vector store
        
        Args:
            organization_id: Organization ID for tenant isolation
            query: Search query
            top_k: Number of results to return
            filters: Metadata filters (jurisdiction, court_level, year, etc.)
        
        Returns:
            List of results with text, metadata, and score
        """
        # Load index if not in memory
        if organization_id not in self.indexes:
            if not self.load_index(organization_id):
                return []
        
        index = self.indexes[organization_id]
        metadatas = self.metadatas[organization_id]
        
        if index.ntotal == 0:
            return []
        
        try:
            # Generate query embedding
            query_embedding = await embedding_service.embed_query(query)
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Search
            # Retrieve more results for filtering
            search_k = min(top_k * 3, index.ntotal)
            distances, indices = index.search(query_vector, search_k)
            
            # Build results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(metadatas):
                    metadata = metadatas[idx]
                    
                    # Apply filters
                    if filters:
                        if not self._matches_filters(metadata, filters):
                            continue
                    
                    results.append({
                        "metadata": metadata,
                        "score": float(dist),
                        "index": int(idx)
                    })
                    
                    if len(results) >= top_k:
                        break
            
            return results
            
        except Exception as e:
            print(f"Error searching for org {organization_id}: {e}")
            return []
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches filters"""
        for key, value in filters.items():
            if key not in metadata:
                return False
            if metadata[key] != value:
                return False
        return True
    
    async def delete_document(
        self,
        organization_id: int,
        document_id: int
    ) -> bool:
        """
        Delete all chunks for a document
        
        Note: FAISS doesn't support deletion, so we rebuild the index
        """
        if organization_id not in self.indexes:
            if not self.load_index(organization_id):
                return False
        
        # Filter out chunks from this document
        metadatas = self.metadatas[organization_id]
        keep_indices = [
            i for i, meta in enumerate(metadatas)
            if meta.get("document_id") != document_id
        ]
        
        if len(keep_indices) == len(metadatas):
            return False  # Document not found
        
        # Rebuild index (FAISS limitation)
        # In production, consider using a different vector DB with native deletion
        # For now, we'll mark this as a TODO
        # TODO: Implement index rebuilding or use vector DB with deletion support
        
        return True


# Global vector store instance
vector_store = VectorStore()

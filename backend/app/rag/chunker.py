"""Document chunker for legal documents"""
from typing import List, Dict, Any
import re
from app.core.config import settings


class LegalDocumentChunker:
    """Chunker optimized for legal documents with hierarchy preservation"""
    
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Pre-compile regex patterns for performance
        self.section_patterns = [
            re.compile(p) for p in [
                r'Section \d+',
                r'Article \d+',
                r'§\s*\d+',
                r'Clause \d+',
                r'\d+\.\s+[A-Z]'
            ]
        ]
        self.split_pattern = re.compile(r'(Section \d+|Article \d+|§\s*\d+|Clause \d+)')
    
    def chunk_document(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Chunk document with legal hierarchy preservation
        
        Args:
            text: Document text
            metadata: Document metadata (jurisdiction, court, etc.)
        
        Returns:
            List of chunks with metadata
        """
        # Try to detect legal structure
        chunks = []
        
        # Check if document has clear section markers
        if self._has_section_markers(text):
            chunks = self._chunk_by_sections(text, metadata)
        else:
            chunks = self._chunk_by_tokens(text, metadata)
        
        return chunks
    
    def _has_section_markers(self, text: str) -> bool:
        """Check if document has section markers"""
        for pattern in self.section_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _chunk_by_sections(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Chunk by legal sections"""
        chunks = []
        
        # Split by section markers
        parts = self.split_pattern.split(text)
        
        current_section = None
        current_text = ""
        
        for part in parts:
            if self.split_pattern.match(part):
                # Save previous section
                if current_text:
                    chunks.extend(
                        self._split_long_text(current_text, metadata, current_section)
                    )
                current_section = part
                current_text = part + "\n"
            else:
                current_text += part
        
        # Save last section
        if current_text:
            chunks.extend(
                self._split_long_text(current_text, metadata, current_section)
            )
        
        return chunks
    
    def _chunk_by_tokens(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Chunk by token count with overlap"""
        chunks = []
        
        # Simple word-based approximation (1 token ≈ 0.75 words)
        words = text.split()
        words_per_chunk = int(self.chunk_size * 0.75)
        words_overlap = int(self.chunk_overlap * 0.75)
        
        start = 0
        chunk_index = 0
        
        while start < len(words):
            end = min(start + words_per_chunk, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = chunk_index
            chunk_metadata["chunk_type"] = "token_based"
            
            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })
            
            chunk_index += 1
            
            if end == len(words):
                break
                
            start = end - words_overlap
            
            # Ensure we make forward progress
            if start <= min(start + words_per_chunk, len(words)) - words_per_chunk:
                 # If check above fails, force advance
                 start += 1
        
        return chunks
    
    def _split_long_text(
        self,
        text: str,
        metadata: Dict[str, Any],
        section_name: str = None
    ) -> List[Dict[str, Any]]:
        """Split long text into smaller chunks"""
        words = text.split()
        words_per_chunk = int(self.chunk_size * 0.75)
        
        if len(words) <= words_per_chunk:
            chunk_metadata = metadata.copy()
            chunk_metadata["section"] = section_name
            return [{
                "text": text,
                "metadata": chunk_metadata
            }]
        
        # Split into multiple chunks
        chunks = []
        words_overlap = int(self.chunk_overlap * 0.75)
        start = 0
        sub_index = 0
        
        while start < len(words):
            end = min(start + words_per_chunk, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            chunk_metadata = metadata.copy()
            chunk_metadata["section"] = section_name
            chunk_metadata["sub_chunk"] = sub_index
            
            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })
            
            sub_index += 1
            start = end - words_overlap
            
            if start >= len(words):
                break
        
        return chunks


# Global chunker instance
legal_chunker = LegalDocumentChunker()

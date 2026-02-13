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
        """Chunk by token count with overlap using memory-efficient generator"""
        chunks = []
        
        # Approximate tokens by splitting on whitespace
        # Use a generator expression if possible, but for simplicity and safety against OOM
        # with huge splits, we'll iterate.
        # Actually, for 136k chars, split() is fine (buffer is ~1MB). 
        # The issue might be the logic loop or the number of small string allocations.
        
        words = text.split()
        total_words = len(words)
        
        if total_words == 0:
            return []
            
        # Target words per chunk (approx 0.75 words per token)
        # Defaults: chunk_size=1000 -> 750 words
        words_per_chunk = int(self.chunk_size * 0.75)
        words_overlap = int(self.chunk_overlap * 0.75)
        
        start = 0
        chunk_index = 0
        
        while start < total_words:
            end = min(start + words_per_chunk, total_words)
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
            
            # Stop if we reached the end
            if end >= total_words:
                break
                
            # Move forward by stride (size - overlap)
            stride = words_per_chunk - words_overlap
            # Ensure stride is at least 1 to avoid infinite loop
            stride = max(1, stride)
            
            start += stride
        
        return chunks
    
    def _split_long_text(
        self,
        text: str,
        metadata: Dict[str, Any],
        section_name: str = None
    ) -> List[Dict[str, Any]]:
        """Split long text into smaller chunks"""
        words = text.split()
        total_words = len(words)
        words_per_chunk = int(self.chunk_size * 0.75)
        
        if total_words <= words_per_chunk:
            chunk_metadata = metadata.copy()
            chunk_metadata["section"] = section_name
            return [{
                "text": text,
                "metadata": chunk_metadata
            }]
        
        # Split into multiple chunks
        chunks = []
        words_overlap = int(self.chunk_overlap * 0.75)
        stride = max(1, words_per_chunk - words_overlap)
        
        start = 0
        sub_index = 0
        
        while start < total_words:
            end = min(start + words_per_chunk, total_words)
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
            
            if end >= total_words:
                break
                
            start += stride
        
        return chunks


# Global chunker instance
legal_chunker = LegalDocumentChunker()

"""Document processor for legal documents"""
import os
from typing import Dict, Any, Optional
from pathlib import Path
import pypdf as PyPDF2
from docx import Document as DocxDocument
from app.core.config import settings


class DocumentProcessor:
    """Processor for extracting text from legal documents"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from document
        
        Args:
            file_path: Path to document file
        
        Returns:
            Extracted text
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif extension == '.docx':
            return self._extract_from_docx(file_path)
        elif extension == '.txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")
        
        return text.strip()
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX"""
        try:
            doc = DocxDocument(file_path)
            text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting DOCX: {str(e)}")
    
    def _extract_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
    
    def extract_metadata(self, text: str, filename: str) -> Dict[str, Any]:
        """
        Extract metadata from document text
        
        This is a simple heuristic-based approach.
        In production, use more sophisticated NER or pattern matching.
        
        Args:
            text: Document text
            filename: Original filename
        
        Returns:
            Extracted metadata
        """
        metadata = {
            "title": filename,
            "jurisdiction": None,
            "year": None,
            "court_level": None
        }
        
        # Simple jurisdiction detection
        jurisdictions = ["US", "UK", "India", "Canada", "Australia"]
        for jurisdiction in jurisdictions:
            if jurisdiction.lower() in text.lower()[:1000]:
                metadata["jurisdiction"] = jurisdiction
                break
        
        # Simple year detection (look for 4-digit years)
        import re
        years = re.findall(r'\b(19\d{2}|20\d{2})\b', text[:2000])
        if years:
            metadata["year"] = int(years[0])
        
        # Simple court level detection
        court_keywords = {
            "supreme_court": ["supreme court", "scotus", "uksc"],
            "high_court": ["high court", "court of appeal"],
            "district_court": ["district court", "county court"]
        }
        
        text_lower = text.lower()[:2000]
        for court_level, keywords in court_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                metadata["court_level"] = court_level
                break
        
        return metadata


# Global document processor instance
document_processor = DocumentProcessor()

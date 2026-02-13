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
            file_path: Path to document file (local path or S3 key)
        
        Returns:
            Extracted text
        """
        from app.services.s3_service import s3_service
        
        # Check if using S3
        temp_file = None
        if s3_service.enabled and not os.path.exists(file_path):
            # Assume file_path is S3 key, download to temp
            import tempfile
            import uuid
            
            suffix = Path(file_path).suffix
            temp_dir = Path(settings.UPLOAD_DIR) / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_path = temp_dir / f"{uuid.uuid4()}{suffix}"
            
            if s3_service.download_file(file_path, str(temp_path)):
                file_path_obj = temp_path
                temp_file = temp_path
            else:
                raise Exception(f"Failed to download file from S3: {file_path}")
        else:
            file_path_obj = Path(file_path)
            
        extension = file_path_obj.suffix.lower()
        
        try:
            if extension == '.pdf':
                text = self._extract_from_pdf(file_path_obj)
            elif extension == '.docx':
                text = self._extract_from_docx(file_path_obj)
            elif extension == '.txt':
                text = self._extract_from_txt(file_path_obj)
            else:
                raise ValueError(f"Unsupported file type: {extension}")
        finally:
            # Clean up temp file
            if temp_file and temp_file.exists():
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
            
        return text
    
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

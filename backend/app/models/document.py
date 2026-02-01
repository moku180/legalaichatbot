"""Document model for legal document storage"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    STATUTE = "statute"
    CASE_LAW = "case_law"
    CONTRACT = "contract"
    REGULATION = "regulation"
    OTHER = "other"


class CourtLevel(str, enum.Enum):
    """Court level enumeration"""
    SUPREME_COURT = "supreme_court"
    HIGH_COURT = "high_court"
    DISTRICT_COURT = "district_court"
    TRIBUNAL = "tribunal"
    NOT_APPLICABLE = "not_applicable"


class Document(Base):
    """Document model with metadata for legal documents"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenancy
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # File information
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)  # .pdf, .docx, .txt
    
    # Legal metadata
    document_type = Column(SQLEnum(DocumentType), default=DocumentType.OTHER, nullable=False)
    jurisdiction = Column(String(100), nullable=True, index=True)  # e.g., "US", "UK", "India"
    court_level = Column(SQLEnum(CourtLevel), default=CourtLevel.NOT_APPLICABLE, nullable=False)
    year = Column(Integer, nullable=True, index=True)
    case_number = Column(String(200), nullable=True)
    title = Column(String(500), nullable=True)
    
    # Processing status
    processed = Column(Boolean, default=False, nullable=False)
    processing_error = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', org_id={self.organization_id}, processed={self.processed})>"

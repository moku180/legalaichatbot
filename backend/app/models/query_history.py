"""Query history model for tracking user queries"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class QueryHistory(Base):
    """Query history model for usage tracking and analytics"""
    __tablename__ = "query_history"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenancy
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Query data
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    
    # Agent routing
    intent_classification = Column(String(100), nullable=True)  # statutory, case_law, contract, etc.
    agents_used = Column(JSON, nullable=True)  # List of agent names
    
    # Citations and confidence
    citations = Column(JSON, nullable=True)  # List of citation objects
    confidence_score = Column(Float, nullable=True)
    
    # Usage metrics
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_estimate = Column(Float, default=0.0)
    
    # Performance
    response_time_ms = Column(Integer, nullable=True)
    
    # Safety flags
    safety_triggered = Column(String(200), nullable=True)  # e.g., "personal_advice_refused"
    jurisdiction_mismatch = Column(String(200), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="query_history")
    user = relationship("User", back_populates="query_history")
    
    def __repr__(self):
        return f"<QueryHistory(id={self.id}, user_id={self.user_id}, tokens={self.total_tokens}, created_at={self.created_at})>"

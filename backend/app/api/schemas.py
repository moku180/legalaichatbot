"""Pydantic schemas for API requests/responses"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    organization_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    organization_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Document schemas
class DocumentUpload(BaseModel):
    jurisdiction: Optional[str] = None
    document_type: Optional[str] = None
    court_level: Optional[str] = None
    year: Optional[int] = None
    title: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_size_bytes: int
    document_type: str
    jurisdiction: Optional[str]
    court_level: str
    year: Optional[int]
    title: Optional[str]
    processed: bool
    processing_status: Optional[str] = "queued"
    chunk_count: int
    uploaded_at: datetime
    processed_at: Optional[datetime]
    processing_error: Optional[str] = None
    
    class Config:
        from_attributes = True


# Chat schemas
class ChatQuery(BaseModel):
    query: str
    jurisdiction: Optional[str] = None
    include_citations: bool = True


class Citation(BaseModel):
    source: str
    text: str
    metadata: Dict[str, Any]


class ChatResponse(BaseModel):
    query_id: int
    query: str
    response: str
    intent: str
    agents_used: List[str]
    citations: List[Citation]
    confidence_score: float
    safety_check: str
    disclaimer: str
    tokens_used: int
    cost_estimate: float
    response_time_ms: int


class QueryHistoryResponse(BaseModel):
    id: int
    query: str
    response: str
    intent_classification: Optional[str]
    confidence_score: Optional[float]
    total_tokens: int
    cost_estimate: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analytics schemas
class UsageStats(BaseModel):
    total_queries: int
    total_tokens: int
    total_cost: float
    avg_confidence: float
    queries_by_intent: Dict[str, int]
    queries_over_time: List[Dict[str, Any]]


class OrganizationResponse(BaseModel):
    id: int
    name: str
    subscription_tier: str
    created_at: datetime
    total_documents: int
    total_queries: int
    
    class Config:
        from_attributes = True

"""User model with RBAC"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class UserRole(str, enum.Enum):
    """User role enumeration for RBAC"""
    ADMIN = "admin"
    LAWYER = "lawyer"
    RESEARCHER = "researcher"
    VIEWER = "viewer"


class User(Base):
    """User model with role-based access control"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Multi-tenancy
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    query_history = relationship("QueryHistory", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}', org_id={self.organization_id})>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    @property
    def can_upload_documents(self) -> bool:
        """Check if user can upload documents"""
        return self.role in [UserRole.ADMIN, UserRole.LAWYER, UserRole.RESEARCHER]
    
    @property
    def can_delete_documents(self) -> bool:
        """Check if user can delete documents"""
        return self.role in [UserRole.ADMIN, UserRole.LAWYER]
    
    @property
    def can_view_analytics(self) -> bool:
        """Check if user can view analytics"""
        return self.role == UserRole.ADMIN

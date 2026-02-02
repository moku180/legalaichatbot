"""Document management API"""
import os
import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, BackgroundTasks

from app.db.base import get_db, AsyncSessionLocal
from sqlalchemy import select, func
from app.core.dependencies import get_current_user, get_current_organization, require_upload_permission
from app.core.config import settings
from app.models.user import User
from app.models.organization import Organization
from app.models.document import Document, DocumentType, CourtLevel
from app.api.schemas import DocumentResponse
from app.rag.document_processor import document_processor
from app.rag.chunker import legal_chunker
from app.rag.vector_store import vector_store

router = APIRouter(prefix="/documents", tags=["documents"])

async def process_document_task(
    document_id: int,
    file_path: str,
    organization_id: int
):
    """Background task to process document"""
    async with AsyncSessionLocal() as db:
        try:
            # Re-fetch document to ensure attached session
            result = await db.execute(select(Document).where(Document.id == document_id))
            document = result.scalar_one_or_none()
            
            if not document:
                return

            # Extract text
            text = document_processor.extract_text(str(file_path))
            
            # Extract metadata if not provided
            if not document.jurisdiction or not document.year:
                extracted_metadata = document_processor.extract_metadata(text, document.filename)
                if not document.jurisdiction:
                    document.jurisdiction = extracted_metadata.get("jurisdiction")
                if not document.year:
                    document.year = extracted_metadata.get("year")
            
            # Chunk document
            chunks = legal_chunker.chunk_document(
                text=text,
                metadata={
                    "document_id": document.id,
                    "organization_id": organization_id,
                    "title": document.title,
                    "jurisdiction": document.jurisdiction,
                    "court_level": document.court_level.value,
                    "year": document.year,
                    "document_type": document.document_type.value
                }
            )
            
            # Add text to chunks for storage
            for chunk in chunks:
                chunk["metadata"]["text"] = chunk["text"]
            
            # Add to vector store
            success = await vector_store.add_documents(
                organization_id=organization_id,
                chunks=chunks
            )
            
            if success:
                document.processed = True
                document.chunk_count = len(chunks)
                from datetime import datetime
                document.processed_at = datetime.utcnow()
            else:
                document.processing_error = "Failed to add to vector store"
            
            await db.commit()
            
        except Exception as e:
            document.processing_error = str(e)
            await db.commit()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    jurisdiction: str = Form(None),
    document_type: str = Form("other"),
    court_level: str = Form("not_applicable"),
    year: int = Form(None),
    title: str = Form(None),
    current_user: User = Depends(require_upload_permission),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Upload legal document"""
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset
    
    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    # Save file
    upload_dir = Path(settings.UPLOAD_DIR) / f"org_{organization.id}"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create document record
    document = Document(
        organization_id=organization.id,
        uploaded_by=current_user.id,
        filename=file.filename,
        file_path=str(file_path),
        file_size_bytes=file_size,
        file_type=file_ext,
        document_type=DocumentType(document_type),
        jurisdiction=jurisdiction,
        court_level=CourtLevel(court_level),
        year=year,
        title=title or file.filename,
        processed=False
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    # Add processing to background tasks
    background_tasks.add_task(
        process_document_task,
        document.id,
        str(file_path),
        organization.id
    )
    
    return document


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    organization: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List organization's documents"""
    
    result = await db.execute(
        select(Document)
        .where(Document.organization_id == organization.id)
        .order_by(Document.uploaded_at.desc())
    )
    documents = result.scalars().all()
    
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    organization: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document details"""
    
    result = await db.execute(
        select(Document)
        .where(
            Document.id == document_id,
            Document.organization_id == organization.id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    organization: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete document"""
    
    if not current_user.can_delete_documents:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete documents"
        )
    
    result = await db.execute(
        select(Document)
        .where(
            Document.id == document_id,
            Document.organization_id == organization.id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception:
        pass
    
    # Delete from vector store (TODO: implement proper deletion)
    # await vector_store.delete_document(organization.id, document_id)
    
    # Delete from database
    await db.delete(document)
    await db.commit()
    
    return None

"""Document Routes"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.security import get_current_user
from app.database import get_db
from app.schemas import DocumentCreate, DocumentUpdate, SectionCreate, SectionUpdate
from app.services import DocumentService

router = APIRouter()


@router.post("/{project_id}/documents", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_document(
    project_id: UUID,
    doc_data: DocumentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create document in project"""
    try:
        document = DocumentService.create_document(
            db, project_id, UUID(current_user["user_id"]), doc_data.dict()
        )
        return {
            "status": "success",
            "data": {
                "document_id": str(document.id),
                "title": document.title,
                "document_type": document.document_type,
                "created_at": document.created_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{document_id}", response_model=dict)
async def get_document(
    document_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document details"""
    try:
        document = DocumentService.get_document(db, document_id, UUID(current_user["user_id"]))
        
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
        return {
            "status": "success",
            "data": {
                "document_id": str(document.id),
                "project_id": str(document.project_id),
                "title": document.title,
                "document_type": document.document_type,
                "config": document.config_json,
                "sections": [
                    {
                        "section_id": str(s.id),
                        "title": s.title,
                        "order": s.section_order,
                        "content_type": s.content_type,
                        "is_generated": s.is_generated
                    }
                    for s in document.sections
                ],
                "created_at": document.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{document_id}/sections", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_section(
    document_id: UUID,
    section_data: SectionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create section in document"""
    try:
        section = DocumentService.create_section(
            db, document_id, UUID(current_user["user_id"]), section_data.dict()
        )
        return {
            "status": "success",
            "data": {
                "section_id": str(section.id),
                "title": section.title,
                "section_order": section.section_order,
                "content_type": section.content_type,
                "is_generated": section.is_generated
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

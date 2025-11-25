"""Project Routes"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.security import get_current_user
from app.database import get_db
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services import ProjectService

router = APIRouter()


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project"""
    try:
        project = ProjectService.create_project(
            db, UUID(current_user["user_id"]), project_data.dict()
        )
        return {
            "status": "success",
            "data": {
                "project_id": str(project.id),
                "title": project.title,
                "status": project.status,
                "created_at": project.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=dict)
async def list_projects(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: str = Query(None, alias="status"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all user projects"""
    try:
        projects, total = ProjectService.list_projects(
            db, UUID(current_user["user_id"]), limit, offset
        )
        
        return {
            "status": "success",
            "data": {
                "projects": [
                    {
                        "project_id": str(p.id),
                        "title": p.title,
                        "status": p.status,
                        "document_type": p.document_type,
                        "created_at": p.created_at.isoformat()
                    }
                    for p in projects
                ],
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{project_id}", response_model=dict)
async def get_project(
    project_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project details"""
    try:
        project = ProjectService.get_project(db, project_id, UUID(current_user["user_id"]))
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return {
            "status": "success",
            "data": {
                "project_id": str(project.id),
                "title": project.title,
                "description": project.description,
                "status": project.status,
                "document_type": project.document_type,
                "documents": [
                    {
                        "document_id": str(d.id),
                        "title": d.title,
                        "type": d.document_type
                    }
                    for d in project.documents
                ],
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{project_id}", response_model=dict)
async def update_project(
    project_id: UUID,
    update_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project"""
    try:
        project = ProjectService.update_project(
            db, project_id, UUID(current_user["user_id"]), update_data.dict(exclude_unset=True)
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return {
            "status": "success",
            "data": {
                "project_id": str(project.id),
                "title": project.title,
                "status": project.status,
                "updated_at": project.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete project"""
    try:
        success = ProjectService.delete_project(db, project_id, UUID(current_user["user_id"]))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

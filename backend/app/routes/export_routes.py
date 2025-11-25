"""Export Routes"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import UUID
import os

from app.core.security import get_current_user
from app.database import get_db
from app.core.config import settings
from app.schemas import ExportRequest
from app.utils.export import ExportService, TemplateService

router = APIRouter()


@router.post("/generate", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def generate_export(
    request: ExportRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate document export"""
    try:
        from app.models import Document, Project, ExportLog
        
        # Verify access
        document = db.query(Document).join(Project).filter(
            Document.id == request.document_id,
            Project.user_id == UUID(current_user["user_id"])
        ).first()
        
        if not document:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        # Prepare sections
        sections = [
            {
                "title": s.title,
                "content": next((gc.content for gc in s.generated_contents if gc.is_approved), "")
            }
            for s in document.sections
        ]
        
        # Generate export
        file_bytes = ExportService.export_document(
            request.document_id,
            sections,
            request.export_format,
            request.export_options,
            project_title=document.project.title
        )
        
        # Save export
        filepath = ExportService.save_export(
            file_bytes,
            request.document_id,
            request.export_format,
            settings.EXPORT_TEMP_DIR
        )
        
        # Log export
        export_log = ExportLog(
            document_id=request.document_id,
            export_format=request.export_format,
            file_size_bytes=len(file_bytes),
            export_status="success",
            export_path=filepath
        )
        db.add(export_log)
        db.commit()
        
        export_job_id = str(export_log.id)
        
        return {
            "status": "success",
            "message": "Export job queued",
            "data": {
                "export_job_id": export_job_id,
                "status": "completed",
                "estimated_time_seconds": 0
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/status/{export_job_id}", response_model=dict)
async def get_export_status(
    export_job_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get export status"""
    try:
        from app.models import ExportLog
        
        export_log = db.query(ExportLog).filter(ExportLog.id == export_job_id).first()
        
        if not export_log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")
        
        return {
            "status": "success",
            "data": {
                "export_job_id": str(export_log.id),
                "document_id": str(export_log.document_id),
                "export_format": export_log.export_format,
                "job_status": export_log.export_status,
                "download_url": f"/api/export/download/{export_log.id}",
                "file_size_bytes": export_log.file_size_bytes,
                "created_at": export_log.created_at.isoformat(),
                "completed_at": (export_log.created_at.isoformat() if export_log.export_status == "success" else None)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/download/{export_job_id}")
async def download_export(
    export_job_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download exported file"""
    try:
        from app.models import ExportLog
        
        export_log = db.query(ExportLog).filter(ExportLog.id == export_job_id).first()
        
        if not export_log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")
        
        if not os.path.exists(export_log.export_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if export_log.export_format == "pptx":
            media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        
        return FileResponse(
            export_log.export_path,
            media_type=media_type,
            filename=f"document.{export_log.export_format}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/templates/outline", response_model=dict)
async def generate_outline_template(
    topic: str = Query(...),
    document_type: str = Query(...),
    num_sections: int = Query(5, ge=2, le=20),
    style: str = Query("professional", regex="^(professional|casual|academic|creative)$"),
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-suggested outline template (bonus feature)"""
    try:
        from app.integrations import get_llm_client
        
        llm_client = get_llm_client()
        outline = TemplateService.generate_outline_template(
            topic, document_type, num_sections, llm_client, style
        )
        
        return {
            "status": "success",
            "data": {
                "outline": outline
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/templates/slide-titles", response_model=dict)
async def generate_slide_titles_template(
    topic: str = Query(...),
    num_slides: int = Query(5, ge=2, le=50),
    audience: str = Query("general"),
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-suggested slide titles (bonus feature)"""
    try:
        from app.integrations import get_llm_client
        
        llm_client = get_llm_client()
        slide_titles = TemplateService.generate_slide_titles_template(
            topic, num_slides, llm_client, audience
        )
        
        return {
            "status": "success",
            "data": {
                "slide_titles": slide_titles
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

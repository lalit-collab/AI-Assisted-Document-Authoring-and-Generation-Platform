"""Content Generation Routes"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
import json

from app.core.security import get_current_user
from app.database import get_db
from app.schemas import GenerationRequest
from app.services import GenerationService

router = APIRouter()


@router.post("/generate", response_model=dict)
async def generate_content(
    request: GenerationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI content for section"""
    try:
        user_id = UUID(current_user["user_id"])
        
        if request.stream:
            async def generate():
                try:
                    async for chunk in await GenerationService.generate_content(
                        db, request.section_id, request.document_id, user_id,
                        request.prompt_overrides, stream=True
                    ):
                        yield chunk
                except Exception as e:
                    yield json.dumps({"error": str(e)}) + "\n"
            
            return StreamingResponse(generate(), media_type="application/x-ndjson")
        else:
            content = await GenerationService.generate_content(
                db, request.section_id, request.document_id, user_id,
                request.prompt_overrides, stream=False
            )
            
            return {
                "status": "success",
                "data": {
                    "content_id": str(content.id),
                    "section_id": str(content.section_id),
                    "content": content.content,
                    "model_used": content.model_used,
                    "tokens_used": content.tokens_used,
                    "generation_time_ms": content.generation_time_ms,
                    "created_at": content.created_at.isoformat()
                }
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/generated-content/{content_id}", response_model=dict)
async def get_generated_content(
    content_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get generated content"""
    try:
        from app.models import GeneratedContent
        
        content = db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
        
        if not content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
        
        return {
            "status": "success",
            "data": {
                "content_id": str(content.id),
                "section_id": str(content.section_id),
                "content": content.content,
                "version": content.version,
                "model_used": content.model_used,
                "tokens_used": content.tokens_used,
                "is_approved": content.is_approved,
                "refinements": [
                    {
                        "refinement_id": str(r.id),
                        "type": r.feedback_type,
                        "text": r.feedback_text
                    }
                    for r in content.refinements
                ],
                "created_at": content.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

"""Refinement Routes"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
import json

from app.core.security import get_current_user
from app.database import get_db
from app.schemas import RefinementRequest, ApplyFeedbackRequest
from app.services import RefinementService, GenerationService

router = APIRouter()


@router.post("/feedback", response_model=dict, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback: RefinementRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback on generated content"""
    try:
        refinement = RefinementService.submit_feedback(
            db, feedback.dict(), UUID(current_user["user_id"])
        )
        
        return {
            "status": "success",
            "data": {
                "refinement_id": str(refinement.id),
                "content_id": str(refinement.generated_content_id),
                "feedback_type": refinement.feedback_type,
                "is_processed": refinement.is_processed,
                "created_at": refinement.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/history/{content_id}", response_model=dict)
async def get_refinement_history(
    content_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get refinement history for content"""
    try:
        from app.models import GeneratedContent
        
        content = db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
        
        if not content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
        
        return {
            "status": "success",
            "data": {
                "content_id": str(content.id),
                "refinements": [
                    {
                        "refinement_id": str(r.id),
                        "feedback_type": r.feedback_type,
                        "refinement_reason": r.refinement_reason,
                        "suggested_changes": r.suggested_changes,
                        "created_at": r.created_at.isoformat()
                    }
                    for r in content.refinements
                ]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/apply-feedback", response_model=dict)
async def apply_feedback(
    request: ApplyFeedbackRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply feedback and regenerate content"""
    try:
        from app.models import GeneratedContent
        
        content = db.query(GeneratedContent).filter(GeneratedContent.id == request.content_id).first()
        
        if not content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
        
        if request.stream:
            async def generate():
                try:
                    # Regenerate with feedback
                    feedback_text = "\n".join([
                        r.feedback_text for r in content.refinements if r.feedback_text
                    ])
                    
                    async for chunk in await GenerationService.generate_content(
                        db, content.section_id, content.section.document_id, 
                        UUID(current_user["user_id"]), 
                        {"feedback": feedback_text},
                        stream=True
                    ):
                        yield chunk
                except Exception as e:
                    yield json.dumps({"error": str(e)}) + "\n"
            
            return StreamingResponse(generate(), media_type="application/x-ndjson")
        else:
            # Non-streaming refinement
            return {
                "status": "success",
                "message": "Feedback applied successfully"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

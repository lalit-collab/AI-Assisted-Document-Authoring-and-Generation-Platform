"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ==================== Authentication Schemas ====================

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(UserBase):
    user_id: UUID
    is_active: bool
    is_email_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Project Schemas ====================

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    document_type: str = Field(..., pattern="^(document|presentation)$")
    metadata: Optional[Dict[str, Any]] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    project_id: UUID
    title: str
    description: Optional[str]
    document_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    documents: List['DocumentResponse'] = []


# ==================== Document Schemas ====================

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    document_type: str = Field(..., pattern="^(word|powerpoint)$")
    config: Dict[str, Any] = Field(default_factory=dict)


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    document_id: UUID
    project_id: UUID
    title: str
    document_type: str
    config: Dict[str, Any]
    current_version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    sections: List['SectionResponse'] = []


# ==================== Section Schemas ====================

class SectionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    section_order: int = Field(..., ge=0)
    content_type: str = Field(..., pattern="^(text|slide|bullet_points)$")
    section_config: Optional[Dict[str, Any]] = None


class SectionUpdate(BaseModel):
    title: Optional[str] = None
    section_order: Optional[int] = None
    content_type: Optional[str] = None
    section_config: Optional[Dict[str, Any]] = None


class SectionResponse(BaseModel):
    section_id: UUID
    document_id: UUID
    title: str
    section_order: int
    content_type: str
    is_generated: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Content Generation Schemas ====================

class GenerationRequest(BaseModel):
    document_id: UUID
    section_id: UUID
    prompt_overrides: Optional[Dict[str, Any]] = None
    stream: bool = False


class GeneratedContentResponse(BaseModel):
    content_id: UUID
    section_id: UUID
    content: str
    version: int
    model_used: str
    tokens_used: int
    generation_time_ms: int
    is_approved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContentChunk(BaseModel):
    type: str  # 'content_chunk' or 'generation_complete'
    content: Optional[str] = None
    content_id: Optional[UUID] = None
    tokens_used: Optional[int] = None


# ==================== Refinement Schemas ====================

class RefinementRequest(BaseModel):
    content_id: UUID
    feedback_type: str = Field(..., pattern="^(like|dislike|comment)$")
    refinement_reason: Optional[str] = None
    suggested_changes: Optional[str] = None
    feedback_text: Optional[str] = None
    regenerate: bool = False


class RefinementResponse(BaseModel):
    refinement_id: UUID
    content_id: UUID
    feedback_type: str
    is_processed: bool
    new_content_id: Optional[UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApplyFeedbackRequest(BaseModel):
    content_id: UUID
    refinement_ids: List[UUID] = []
    stream: bool = False


# ==================== Export Schemas ====================

class ExportRequest(BaseModel):
    document_id: UUID
    export_format: str = Field(..., pattern="^(docx|pptx)$")
    export_options: Optional[Dict[str, Any]] = None


class ExportStatusResponse(BaseModel):
    export_job_id: UUID
    document_id: UUID
    export_format: str
    job_status: str  # 'processing', 'completed', 'failed'
    download_url: Optional[str] = None
    file_size_bytes: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ExportJobResponse(BaseModel):
    export_job_id: UUID
    status: str  # 'processing', 'completed', 'failed'
    estimated_time_seconds: Optional[int] = None


# ==================== Template Schemas (Bonus Feature) ====================

class TemplateGenerationRequest(BaseModel):
    """Request to generate AI-suggested templates"""
    document_type: str  # 'document' or 'presentation'
    topic: str
    num_sections: int = Field(..., ge=2, le=20)
    style: Optional[str] = None


class TemplateResponse(BaseModel):
    """AI-generated template suggestion"""
    outline: List[Dict[str, str]]  # [{"title": "...", "description": "..."}, ...]
    slide_titles: Optional[List[str]] = None  # For presentations
    metadata: Dict[str, Any] = {}


# ==================== Error Schemas ====================

class ErrorDetail(BaseModel):
    field: str
    error: str


class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None


# Update forward references
ProjectDetailResponse.update_forward_refs()
DocumentDetailResponse.update_forward_refs()

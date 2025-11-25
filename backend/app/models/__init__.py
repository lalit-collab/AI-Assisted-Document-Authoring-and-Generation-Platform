"""Database Models"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, JSON, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime
import enum

Base = declarative_base()


class User(Base):
    """User model for authentication and profile"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile_picture_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    document_type = Column(String(50))  # 'document' or 'presentation'
    status = Column(String(50), default="draft")  # 'draft', 'in_progress', 'completed'
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")


class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    document_type = Column(String(50))  # 'word', 'powerpoint'
    config_json = Column(JSON, nullable=False)
    current_version = Column(Integer, default=1)
    is_template = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    sections = relationship("Section", back_populates="document", cascade="all, delete-orphan")


class Section(Base):
    """Document section model"""
    __tablename__ = "sections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    section_order = Column(Integer, nullable=False)
    content_type = Column(String(50))  # 'text', 'slide', 'bullet_points'
    section_config_json = Column(JSON)
    is_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="sections")
    generated_contents = relationship("GeneratedContent", back_populates="section", cascade="all, delete-orphan")


class GeneratedContent(Base):
    """Generated content snapshots"""
    __tablename__ = "generated_content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    content_format = Column(String(50))  # 'markdown', 'html', 'plain_text'
    version = Column(Integer, default=1)
    model_used = Column(String(100))  # 'gemini-pro', 'gpt-4', etc.
    prompt_used = Column(Text)
    tokens_used = Column(Integer)
    generation_time_ms = Column(Integer)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    section = relationship("Section", back_populates="generated_contents")
    refinements = relationship("Refinement", back_populates="generated_content", cascade="all, delete-orphan")


class Refinement(Base):
    """User feedback and refinement records"""
    __tablename__ = "refinements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generated_content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id", ondelete="CASCADE"), nullable=False)
    feedback_type = Column(String(50))  # 'like', 'dislike', 'comment'
    feedback_text = Column(Text)
    refinement_reason = Column(String(50))  # 'too_long', 'unclear', 'off_topic', 'other'
    suggested_changes = Column(Text)
    is_processed = Column(Boolean, default=False)
    regenerated_content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    generated_content = relationship("GeneratedContent", back_populates="refinements", foreign_keys=[generated_content_id])


class ExportLog(Base):
    """Export operation logs"""
    __tablename__ = "export_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    export_format = Column(String(50))  # 'docx', 'pptx'
    file_size_bytes = Column(Integer)
    export_status = Column(String(50))  # 'success', 'failed', 'in_progress'
    error_message = Column(Text)
    export_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Audit trail for system actions"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100))  # 'create_project', 'generate_content', 'export', etc.
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    details_json = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class APIKey(Base):
    """API keys for LLM providers"""
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50))  # 'gemini', 'openai'
    encrypted_key = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

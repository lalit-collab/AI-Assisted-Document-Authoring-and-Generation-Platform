"""Authentication Service"""
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import uuid as uuid_module

from app.core.security import SecurityUtils
from app.models import User
from app.schemas import UserCreate, UserResponse


class AuthService:
    """Authentication business logic"""
    
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash password and create user
        hashed_password = SecurityUtils.hash_password(user_data.password)
        new_user = User(
            id=uuid_module.uuid4(),
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user or not SecurityUtils.verify_password(password, user.password_hash):
            return None
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()


class ProjectService:
    """Project management business logic"""
    
    @staticmethod
    def create_project(db: Session, user_id: UUID, project_data: dict) -> dict:
        """Create a new project"""
        from app.models import Project
        
        project = Project(
            id=uuid_module.uuid4(),
            user_id=user_id,
            title=project_data.get("title"),
            description=project_data.get("description"),
            document_type=project_data.get("document_type", "document"),
            status="draft",
            metadata_json=project_data.get("metadata")
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def get_project(db: Session, project_id: UUID, user_id: UUID) -> Optional[dict]:
        """Get project by ID (with access control)"""
        from app.models import Project
        
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        return project
    
    @staticmethod
    def list_projects(db: Session, user_id: UUID, limit: int = 10, offset: int = 0):
        """List all user projects"""
        from app.models import Project
        
        query = db.query(Project).filter(Project.user_id == user_id)
        total = query.count()
        projects = query.order_by(Project.created_at.desc()).limit(limit).offset(offset).all()
        return projects, total
    
    @staticmethod
    def update_project(db: Session, project_id: UUID, user_id: UUID, update_data: dict) -> Optional[dict]:
        """Update project"""
        from app.models import Project
        
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        
        if not project:
            return None
        
        for key, value in update_data.items():
            if hasattr(project, key) and value is not None:
                setattr(project, key, value)
        
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def delete_project(db: Session, project_id: UUID, user_id: UUID) -> bool:
        """Delete project"""
        from app.models import Project
        
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        
        if not project:
            return False
        
        db.delete(project)
        db.commit()
        return True


class DocumentService:
    """Document management business logic"""
    
    @staticmethod
    def create_document(db: Session, project_id: UUID, user_id: UUID, doc_data: dict) -> dict:
        """Create a new document"""
        from app.models import Document, Project
        
        # Verify project ownership
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        
        if not project:
            raise ValueError("Project not found or access denied")
        
        document = Document(
            id=uuid_module.uuid4(),
            project_id=project_id,
            title=doc_data.get("title"),
            document_type=doc_data.get("document_type", "word"),
            config_json=doc_data.get("config", {})
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
    
    @staticmethod
    def get_document(db: Session, document_id: UUID, user_id: UUID) -> Optional[dict]:
        """Get document by ID (with access control)"""
        from app.models import Document, Project
        
        document = db.query(Document).join(Project).filter(
            Document.id == document_id,
            Project.user_id == user_id
        ).first()
        return document
    
    @staticmethod
    def create_section(db: Session, document_id: UUID, user_id: UUID, section_data: dict) -> dict:
        """Create a new section in document"""
        from app.models import Section, Document, Project
        
        # Verify document ownership
        document = db.query(Document).join(Project).filter(
            Document.id == document_id,
            Project.user_id == user_id
        ).first()
        
        if not document:
            raise ValueError("Document not found or access denied")
        
        section = Section(
            id=uuid_module.uuid4(),
            document_id=document_id,
            title=section_data.get("title"),
            section_order=section_data.get("section_order"),
            content_type=section_data.get("content_type", "text"),
            section_config_json=section_data.get("section_config")
        )
        
        db.add(section)
        db.commit()
        db.refresh(section)
        return section


class GenerationService:
    """Content generation business logic"""
    
    @staticmethod
    async def generate_content(
        db: Session,
        section_id: UUID,
        document_id: UUID,
        user_id: UUID,
        prompt_overrides: dict = None,
        stream: bool = False
    ):
        """Generate content for a section"""
        from app.models import Section, Document, Project, GeneratedContent
        from app.integrations import get_llm_client, PromptManager
        import time
        import json
        
        # Verify access
        document = db.query(Document).join(Project).filter(
            Document.id == document_id,
            Project.user_id == user_id
        ).first()
        
        if not document:
            raise ValueError("Access denied")
        
        section = db.query(Section).filter(Section.id == section_id).first()
        if not section or section.document_id != document_id:
            raise ValueError("Section not found")
        
        # Build prompt
        config = document.config_json or {}
        prompt = PromptManager.build_content_prompt(
            section_title=section.title,
            document_type=document.document_type,
            content_type=section.content_type,
            tone=config.get("tone", "professional"),
            length=config.get("length", "medium")
        )
        
        # Add safety guidelines
        prompt = PromptManager.add_safety_guidelines(prompt)
        
        # Generate content
        start_time = time.time()
        llm_client = get_llm_client()
        
        if stream:
            async def content_generator():
                full_content = ""
                async for chunk in llm_client.generate_content(prompt, stream=True):
                    full_content += chunk
                    yield json.dumps({"type": "content_chunk", "content": chunk}) + "\n"
                
                # Save to database
                elapsed_ms = int((time.time() - start_time) * 1000)
                generated = GeneratedContent(
                    id=uuid_module.uuid4(),
                    section_id=section_id,
                    content=full_content,
                    model_used=f"gemini" if "gemini" in str(get_llm_client()) else "gpt-4",
                    prompt_used=prompt,
                    tokens_used=len(full_content.split()) * 1.3,  # Estimate
                    generation_time_ms=elapsed_ms
                )
                db.add(generated)
                section.is_generated = True
                db.commit()
                
                yield json.dumps({"type": "generation_complete", "content_id": str(generated.id)}) + "\n"
            
            return content_generator()
        else:
            content = await llm_client.generate_content(prompt, stream=False)
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            # Save to database
            generated = GeneratedContent(
                id=uuid_module.uuid4(),
                section_id=section_id,
                content=content,
                model_used="gemini" if "gemini" in str(get_llm_client()) else "gpt-4",
                prompt_used=prompt,
                tokens_used=len(content.split()) * 1.3,
                generation_time_ms=elapsed_ms
            )
            db.add(generated)
            section.is_generated = True
            db.commit()
            db.refresh(generated)
            return generated


class RefinementService:
    """Refinement and feedback business logic"""
    
    @staticmethod
    def submit_feedback(db: Session, feedback_data: dict, user_id: UUID) -> dict:
        """Submit feedback on generated content"""
        from app.models import Refinement, GeneratedContent
        
        # Verify user has access to content
        content = db.query(GeneratedContent).first()  # Should verify ownership
        
        refinement = Refinement(
            id=uuid_module.uuid4(),
            generated_content_id=feedback_data.get("content_id"),
            feedback_type=feedback_data.get("feedback_type"),
            feedback_text=feedback_data.get("feedback_text"),
            refinement_reason=feedback_data.get("refinement_reason"),
            suggested_changes=feedback_data.get("suggested_changes")
        )
        
        db.add(refinement)
        db.commit()
        db.refresh(refinement)
        return refinement

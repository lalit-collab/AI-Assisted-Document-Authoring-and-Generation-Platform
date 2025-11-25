# AI-Assisted Document Authoring & Generation Platform - System Design

## Executive Summary

The AI-Assisted Document Authoring & Generation Platform is a sophisticated, full-stack application that leverages Large Language Models (LLMs) to automate the creation of professional documents and presentations. Users can define document outlines, configure generation parameters, and leverage AI to create slide content, which can then be refined through an intuitive feedback loop before exporting to industry-standard formats (Word, PowerPoint).

### Key Features
- **User Authentication**: Secure JWT/Firebase-based authentication
- **Project Management**: Create and manage multiple document projects
- **Document Configuration**: Define document structures, sections, and customization parameters
- **AI-Powered Content Generation**: Leverage Gemini/OpenAI APIs for intelligent content creation
- **Interactive Refinement**: Like/dislike/comment feedback loop for content improvement
- **Multi-format Export**: Export to .docx (Word) and .pptx (PowerPoint) with professional formatting
- **Bonus Feature**: AI-generated outline and slide-title templates

### Technology Stack
- **Backend**: FastAPI, Python 3.9+, PostgreSQL
- **Frontend**: React 18+, Redux/Context API, Material-UI/Tailwind CSS
- **LLM Integration**: Gemini API or OpenAI API
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Document Export**: python-docx, python-pptx
- **Authentication**: JWT tokens, Firebase Auth (optional)
- **Deployment**: Docker, AWS/Heroku/Railway

---

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React Frontend (Web Application)                         │   │
│  │  ├─ Login & Authentication Pages                         │   │
│  │  ├─ Dashboard & Project Management                       │   │
│  │  ├─ Document Configuration                              │   │
│  │  ├─ AI Generation Interface                             │   │
│  │  ├─ Refinement Interface                                │   │
│  │  └─ Export & Download                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬──────────────────────────────────────┘
                             │ HTTPS/REST API
┌────────────────────────────▼──────────────────────────────────────┐
│                    API Gateway & Security Layer                    │
│  ├─ JWT Authentication & Authorization                            │
│  ├─ Rate Limiting & Throttling                                   │
│  ├─ Request Validation & CORS                                    │
│  └─ Error Handling & Logging                                     │
└────────────────────────────┬──────────────────────────────────────┘
                             │
┌────────────────────────────▼──────────────────────────────────────┐
│                     FastAPI Backend Layer                          │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ Route Layer                                              │    │
│  │ ├─ auth_routes.py (Login, Register, Token Refresh)     │    │
│  │ ├─ project_routes.py (CRUD operations)                 │    │
│  │ ├─ document_routes.py (Config & Structure)             │    │
│  │ ├─ generation_routes.py (AI Generation)                │    │
│  │ ├─ refinement_routes.py (Feedback & Refinement)        │    │
│  │ └─ export_routes.py (Document Export)                  │    │
│  └──────────────────────────────────────────────────────────┘    │
│                             │                                     │
│  ┌──────────────────────────▼──────────────────────────────┐    │
│  │ Service Layer                                            │    │
│  │ ├─ AuthService (JWT, password hashing)                 │    │
│  │ ├─ ProjectService (CRUD, access control)               │    │
│  │ ├─ DocumentService (Structure management)              │    │
│  │ ├─ GenerationService (LLM prompting, streaming)        │    │
│  │ ├─ RefinementService (Feedback processing)             │    │
│  │ └─ ExportService (.docx, .pptx generation)             │    │
│  └──────────────────────────────────────────────────────────┘    │
│                             │                                     │
│  ┌──────────────────────────▼──────────────────────────────┐    │
│  │ Integration Layer                                        │    │
│  │ ├─ LLMClient (Gemini/OpenAI API)                        │    │
│  │ ├─ PromptManager (Template & Engineering)              │    │
│  │ └─ CacheManager (Redis/In-Memory)                       │    │
│  └──────────────────────────────────────────────────────────┘    │
│                             │                                     │
│  ┌──────────────────────────▼──────────────────────────────┐    │
│  │ Data Access Layer (Repository Pattern)                  │    │
│  │ ├─ UserRepository                                       │    │
│  │ ├─ ProjectRepository                                    │    │
│  │ ├─ DocumentRepository                                   │    │
│  │ ├─ GenerationRepository                                 │    │
│  │ ├─ RefinementRepository                                 │    │
│  │ └─ AuditRepository                                      │    │
│  └──────────────────────────────────────────────────────────┘    │
└────────────────────────────┬──────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼─────────┐  ┌──────▼────────┐
│  PostgreSQL    │  │  Redis Cache     │  │  LLM APIs    │
│  Database      │  │  (Optional)      │  │  (Gemini/    │
│  ├─ Users      │  │  Session Store   │  │   OpenAI)    │
│  ├─ Projects   │  │  Rate Limits     │  │              │
│  ├─ Documents  │  │  Temp Data       │  │              │
│  ├─ Generations│  │                  │  │              │
│  ├─ Refinements│  │                  │  │              │
│  └─ Audit Logs │  │                  │  │              │
└────────────────┘  └──────────────────┘  └───────────────┘
```

---

## 2. Component-Level Architecture

### 2.1 Frontend Components

#### Authentication Module
- **LoginPage**: Email/password login with error handling
- **RegisterPage**: User registration with validation
- **ForgotPasswordPage**: Password reset flow
- **TokenManager**: JWT token storage and refresh logic

#### Project Management Module
- **DashboardPage**: List all user projects with filters
- **ProjectCreationForm**: Create new projects with metadata
- **ProjectDetailsPage**: View project information and statistics

#### Document Configuration Module
- **OutlineBuilder**: Interactive outline creator with drag-and-drop
- **SectionConfig**: Configure section-specific parameters
- **StylePreferencesPanel**: Define formatting preferences

#### AI Generation Module
- **GenerationScreen**: Monitor real-time content generation with progress
- **PromptPreview**: Display and edit generation prompts
- **SectionGenerationForm**: Configure per-section generation parameters

#### Refinement Module
- **RefinementInterface**: Display generated content with like/dislike buttons
- **CommentPanel**: Add comments and suggested changes
- **FeedbackHistory**: Track all feedback iterations

#### Export Module
- **ExportScreen**: Choose export format (Word/PowerPoint)
- **ExportOptionsPanel**: Customize export settings
- **DownloadManager**: Handle file downloads

### 2.2 Backend Components

#### Authentication Service
- User registration and login
- JWT token generation and validation
- Password hashing with bcrypt
- Rate limiting on auth endpoints

#### Project Service
- Create, read, update, delete projects
- Access control and permissions
- Project statistics and metadata

#### Document Service
- Manage document structures and sections
- Store configuration parameters
- Handle document versions

#### Generation Service
- Interface with LLM APIs
- Manage prompt templates
- Handle streaming responses
- Generate section content and slide titles
- Implement bonus feature (AI-generated templates)

#### Refinement Service
- Store user feedback (like, dislike, comments)
- Regenerate content based on feedback
- Track refinement history

#### Export Service
- Generate .docx files with python-docx
- Generate .pptx files with python-pptx
- Apply styling and formatting
- Handle pagination

### 2.3 Database Components

- **User**: Authentication and profile information
- **Project**: Project metadata and ownership
- **Document**: Document configuration and structure
- **Section**: Individual sections within documents
- **GeneratedContent**: LLM-generated content snapshots
- **Refinement**: User feedback and refinement records
- **AuditLog**: System activity logging

---

## 3. Database Schema

### 3.1 ER Diagram (Conceptual)

```
┌─────────────┐
│    User     │
├─────────────┤
│ id (PK)     │
│ email       │
│ password    │
│ name        │
│ created_at  │
│ updated_at  │
└─────────────┘
      │ 1
      │
      ├─M──────────────────────┐
      │                        │
      │                   ┌──────────────┐
      │                   │  Project     │
      │                   ├──────────────┤
      │                   │ id (PK)      │
      │                   │ user_id (FK) │
      │                   │ title        │
      │                   │ description  │
      │                   │ status       │
      │                   │ created_at   │
      │                   └──────────────┘
      │                        │ 1
      │                        │
      │                        ├─M─────────────────────┐
      │                        │                       │
      │                   ┌──────────────┐      ┌──────────────┐
      │                   │  Document    │      │   Section    │
      │                   ├──────────────┤      ├──────────────┤
      │                   │ id (PK)      │      │ id (PK)      │
      │                   │ project_id   │      │ doc_id (FK)  │
      │                   │ title        │      │ title        │
      │                   │ type         │      │ order        │
      │                   │ config_json  │      │ content_type │
      │                   └──────────────┘      └──────────────┘
      │                                              │ 1
      │                                              │
      │                                              ├─M──────────────┐
      │                                              │                │
      │                                        ┌──────────────┐  ┌───────────┐
      │                                        │GeneratedContent
      │                                        ├──────────────┤  │Refinement │
      │                                        │ id (PK)      │  ├───────────┤
      │                                        │ section_id   │  │ id (PK)   │
      │                                        │ content      │  │ gen_id    │
      │                                        │ version      │  │ feedback  │
      │                                        │ prompt_used  │  │ type      │
      │                                        │ model        │  │ created_at│
      │                                        │ tokens_used  │  └───────────┘
      │                                        │ created_at   │
      │                                        └──────────────┘
      │
      └─M──────────────┐
                       │
                  ┌──────────────┐
                  │  AuditLog    │
                  ├──────────────┤
                  │ id (PK)      │
                  │ user_id (FK) │
                  │ action       │
                  │ resource     │
                  │ timestamp    │
                  │ ip_address   │
                  └──────────────┘
```

### 3.2 Table Definitions

#### `users` Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    profile_picture_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `projects` Table
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    document_type VARCHAR(50), -- 'document' or 'presentation'
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'in_progress', 'completed'
    metadata_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `documents` Table
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    document_type VARCHAR(50), -- 'word', 'powerpoint'
    config_json JSONB NOT NULL, -- Stores generation config, style preferences
    current_version INTEGER DEFAULT 1,
    is_template BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `sections` Table
```sql
CREATE TABLE sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    section_order INTEGER NOT NULL,
    content_type VARCHAR(50), -- 'text', 'slide', 'bullet_points'
    section_config_json JSONB, -- Section-specific generation parameters
    is_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `generated_content` Table
```sql
CREATE TABLE generated_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    section_id UUID NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    content_format VARCHAR(50), -- 'markdown', 'html', 'plain_text'
    version INTEGER NOT NULL DEFAULT 1,
    model_used VARCHAR(100), -- 'gemini-pro', 'gpt-4', etc.
    prompt_used TEXT,
    tokens_used INTEGER,
    generation_time_ms INTEGER,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `refinements` Table
```sql
CREATE TABLE refinements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generated_content_id UUID NOT NULL REFERENCES generated_content(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50), -- 'like', 'dislike', 'comment'
    feedback_text TEXT,
    refinement_reason VARCHAR(50), -- 'too_long', 'unclear', 'off_topic', 'other'
    suggested_changes TEXT,
    is_processed BOOLEAN DEFAULT FALSE,
    regenerated_content_id UUID REFERENCES generated_content(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `export_logs` Table
```sql
CREATE TABLE export_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    export_format VARCHAR(50), -- 'docx', 'pptx'
    file_size_bytes INTEGER,
    export_status VARCHAR(50), -- 'success', 'failed', 'in_progress'
    error_message TEXT,
    export_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `audit_logs` Table
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100), -- 'create_project', 'generate_content', 'export'
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    details_json JSONB,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `api_keys` Table
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50), -- 'gemini', 'openai'
    encrypted_key VARCHAR(500) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Request/Response Flow Diagrams

### 4.1 User Registration Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/auth/register
       │ { email, password, name }
       │
       ▼
┌──────────────────────────────────────┐
│  FastAPI Auth Routes                 │
│  ├─ Validate input schema             │
│  ├─ Check email uniqueness            │
│  └─ Hash password with bcrypt         │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  User Service                        │
│  ├─ Create user record                │
│  └─ Log to audit trail                │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  PostgreSQL Database                 │
│  INSERT INTO users (...)              │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Response to Client                  │
│  {                                    │
│    "status": "success",               │
│    "message": "User created",         │
│    "data": {                          │
│      "user_id": "uuid",               │
│      "email": "user@email.com"        │
│    }                                  │
│  }                                    │
└──────────────────────────────────────┘
```

### 4.2 Document Generation Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/generation/generate
       │ { document_id, section_id, prompt_overrides }
       │
       ▼
┌──────────────────────────────────────┐
│  Generation Routes                   │
│  ├─ Validate user authorization      │
│  ├─ Rate limit check                  │
│  └─ Validate request schema           │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Generation Service                  │
│  ├─ Load document config              │
│  ├─ Load section details              │
│  └─ Build generation prompt           │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Prompt Manager                      │
│  ├─ Apply prompt template             │
│  ├─ Inject context variables          │
│  └─ Add safety guidelines             │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  LLM Client (Gemini/OpenAI)          │
│  ├─ Send prompt to API                │
│  ├─ Handle streaming response         │
│  └─ Parse and validate output         │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Content Validation                  │
│  ├─ Check content length              │
│  ├─ Validate formatting               │
│  └─ Scan for quality issues           │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Data Access Layer                   │
│  INSERT INTO generated_content (...)  │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Response to Client (Streaming)      │
│  Chunk 1: { content: "Introduction"} │
│  Chunk 2: { content: " to AI..."}    │
│  Final: { status: "complete", id }   │
└──────────────────────────────────────┘
```

### 4.3 Refinement & Feedback Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/refinement/feedback
       │ { content_id, type: 'like'|'dislike'|'comment', text? }
       │
       ▼
┌──────────────────────────────────────┐
│  Refinement Routes                   │
│  ├─ Validate authorization            │
│  └─ Store feedback record             │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Refinement Service                  │
│  ├─ Analyze feedback type             │
│  ├─ Build refinement prompt           │
│  └─ Prepare regeneration params       │
└──────┬───────────────────────────────┘
       │
       ├─── If 'like': Skip regeneration
       │
       └─── If 'dislike' or 'comment':
           │
           ▼
           ┌──────────────────────────┐
           │ LLM Generation (again)   │
           │ with refined prompt      │
           └──────┬───────────────────┘
                  │
                  ▼
           ┌──────────────────────────┐
           │ Store new version        │
           │ Link to refinement       │
           └──────┬───────────────────┘
                  │
                  ▼
           ┌──────────────────────────┐
           │ Return new content       │
           └──────────────────────────┘
```

### 4.4 Document Export Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/export/generate
       │ { document_id, format: 'docx'|'pptx', options }
       │
       ▼
┌──────────────────────────────────────┐
│  Export Routes                       │
│  ├─ Validate user authorization      │
│  ├─ Queue export job                 │
│  └─ Return job ID                    │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Export Service (Async Task)         │
│  ├─ Load all sections & content      │
│  ├─ Load styling config              │
│  └─ Instantiate document exporter    │
└──────┬───────────────────────────────┘
       │
       ├─── For .docx (python-docx):
       │    ├─ Create Document object
       │    ├─ Add title & metadata
       │    ├─ For each section:
       │    │  ├─ Add heading
       │    │  ├─ Add content (paragraphs)
       │    │  ├─ Apply styling
       │    │  └─ Add page breaks
       │    └─ Save to temp file
       │
       └─── For .pptx (python-pptx):
           ├─ Create Presentation
           ├─ Add title slide
           ├─ For each section:
           │  ├─ Create slide layout
           │  ├─ Add title text box
           │  ├─ Add content text box
           │  ├─ Apply formatting
           │  └─ Add bullet points
           └─ Save to temp file
       │
       ▼
┌──────────────────────────────────────┐
│  File Upload (Optional)              │
│  ├─ Upload to S3/Cloud Storage      │
│  └─ Generate download URL            │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Response to Client                  │
│  {                                    │
│    "status": "success",               │
│    "download_url": "s3://...",       │
│    "file_size": 1024000               │
│  }                                    │
└──────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Client    │
│  (Downloads)│
└─────────────┘
```

---

## 5. API Specifications

### 5.1 Authentication Endpoints

#### POST /api/auth/register
**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John"
  }
}
```

**Error Response (400):**
```json
{
  "status": "error",
  "error_code": "VALIDATION_ERROR",
  "message": "Email already exists or password too weak",
  "details": [
    {
      "field": "email",
      "error": "Email already registered"
    }
  ]
}
```

#### POST /api/auth/login
**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "first_name": "John"
    }
  }
}
```

#### POST /api/auth/refresh
**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600
  }
}
```

### 5.2 Project Management Endpoints

#### POST /api/projects
**Request:**
```json
{
  "title": "Q4 Marketing Report",
  "description": "Annual marketing performance report",
  "document_type": "document",
  "metadata": {
    "industry": "technology",
    "target_audience": "executives"
  }
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Q4 Marketing Report",
    "status": "draft",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### GET /api/projects
**Query Parameters:**
- `limit`: 10 (default)
- `offset`: 0 (default)
- `status`: draft|in_progress|completed (optional)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "projects": [
      {
        "project_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Q4 Marketing Report",
        "status": "draft",
        "document_type": "document",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 1,
    "limit": 10,
    "offset": 0
  }
}
```

#### GET /api/projects/{project_id}
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Q4 Marketing Report",
    "description": "Annual marketing performance report",
    "status": "draft",
    "document_type": "document",
    "documents": [
      {
        "document_id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "Main Report",
        "type": "word"
      }
    ],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

#### PUT /api/projects/{project_id}
**Request:**
```json
{
  "title": "Q4 Marketing Report - Updated",
  "status": "in_progress"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Q4 Marketing Report - Updated",
    "status": "in_progress",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

#### DELETE /api/projects/{project_id}
**Response (204):**
```
No Content
```

**Error Response (404):**
```json
{
  "status": "error",
  "error_code": "NOT_FOUND",
  "message": "Project not found"
}
```

### 5.3 Document Configuration Endpoints

#### POST /api/projects/{project_id}/documents
**Request:**
```json
{
  "title": "Main Report",
  "document_type": "word",
  "config": {
    "tone": "professional",
    "length": "medium",
    "language": "English",
    "style_preferences": {
      "font": "Calibri",
      "font_size": 12,
      "line_spacing": 1.5,
      "color_scheme": "professional"
    }
  }
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "document_id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Main Report",
    "document_type": "word",
    "config": { ... },
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### GET /api/documents/{document_id}
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "document_id": "550e8400-e29b-41d4-a716-446655440001",
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Main Report",
    "document_type": "word",
    "config": { ... },
    "sections": [
      {
        "section_id": "550e8400-e29b-41d4-a716-446655440002",
        "title": "Executive Summary",
        "order": 1,
        "content_type": "text",
        "is_generated": false
      }
    ],
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### POST /api/documents/{document_id}/sections
**Request:**
```json
{
  "title": "Executive Summary",
  "section_order": 1,
  "content_type": "text",
  "section_config": {
    "focus_points": ["key achievements", "major challenges"],
    "max_length": 500
  }
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "section_id": "550e8400-e29b-41d4-a716-446655440002",
    "title": "Executive Summary",
    "section_order": 1,
    "content_type": "text",
    "is_generated": false
  }
}
```

### 5.4 AI Generation Endpoints

#### POST /api/generation/generate
**Request:**
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440001",
  "section_id": "550e8400-e29b-41d4-a716-446655440002",
  "prompt_overrides": {
    "custom_instructions": "Focus on financial metrics and ROI"
  },
  "stream": true
}
```

**Response (200 - Streaming):**
```
data: {"type": "content_chunk", "content": "The executive summary"}
data: {"type": "content_chunk", "content": " provides an overview of"}
data: {"type": "generation_complete", "content_id": "550e8400...", "tokens_used": 156}
```

**Response (200 - Non-streaming):**
```json
{
  "status": "success",
  "data": {
    "content_id": "550e8400-e29b-41d4-a716-446655440003",
    "section_id": "550e8400-e29b-41d4-a716-446655440002",
    "content": "The executive summary provides a comprehensive overview...",
    "model_used": "gemini-pro",
    "tokens_used": 156,
    "generation_time_ms": 2345,
    "created_at": "2024-01-15T10:35:00Z"
  }
}
```

#### GET /api/generation/generated-content/{content_id}
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "content_id": "550e8400-e29b-41d4-a716-446655440003",
    "section_id": "550e8400-e29b-41d4-a716-446655440002",
    "content": "The executive summary provides a comprehensive overview...",
    "version": 1,
    "model_used": "gemini-pro",
    "tokens_used": 156,
    "is_approved": false,
    "refinements": [
      {
        "refinement_id": "550e8400-e29b-41d4-a716-446655440004",
        "type": "comment",
        "text": "Add more specific numbers"
      }
    ],
    "created_at": "2024-01-15T10:35:00Z"
  }
}
```

### 5.5 Refinement Endpoints

#### POST /api/refinement/feedback
**Request:**
```json
{
  "content_id": "550e8400-e29b-41d4-a716-446655440003",
  "feedback_type": "dislike",
  "refinement_reason": "too_long",
  "suggested_changes": "Reduce to 200 words maximum",
  "regenerate": true
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "refinement_id": "550e8400-e29b-41d4-a716-446655440004",
    "content_id": "550e8400-e29b-41d4-a716-446655440003",
    "feedback_type": "dislike",
    "is_processed": false,
    "new_content_id": null,
    "created_at": "2024-01-15T10:40:00Z"
  }
}
```

#### GET /api/refinement/history/{content_id}
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "content_id": "550e8400-e29b-41d4-a716-446655440003",
    "refinements": [
      {
        "refinement_id": "550e8400-e29b-41d4-a716-446655440004",
        "feedback_type": "dislike",
        "refinement_reason": "too_long",
        "suggested_changes": "Reduce to 200 words",
        "created_at": "2024-01-15T10:40:00Z"
      }
    ]
  }
}
```

#### POST /api/refinement/apply-feedback
**Request:**
```json
{
  "content_id": "550e8400-e29b-41d4-a716-446655440003",
  "refinement_ids": ["550e8400-e29b-41d4-a716-446655440004"],
  "stream": true
}
```

**Response (200 - Streaming):**
```
data: {"type": "content_chunk", "content": "Refined content..."}
data: {"type": "generation_complete", "new_content_id": "550e8400..."}
```

### 5.6 Export Endpoints

#### POST /api/export/generate
**Request:**
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440001",
  "export_format": "docx",
  "export_options": {
    "include_toc": true,
    "include_page_numbers": true,
    "include_timestamps": false,
    "theme": "professional"
  }
}
```

**Response (202 Accepted):**
```json
{
  "status": "success",
  "message": "Export job queued",
  "data": {
    "export_job_id": "550e8400-e29b-41d4-a716-446655440005",
    "status": "processing",
    "estimated_time_seconds": 30
  }
}
```

#### GET /api/export/status/{export_job_id}
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "export_job_id": "550e8400-e29b-41d4-a716-446655440005",
    "document_id": "550e8400-e29b-41d4-a716-446655440001",
    "export_format": "docx",
    "job_status": "completed",
    "download_url": "https://cdn.example.com/exports/file_123.docx",
    "file_size_bytes": 1024000,
    "created_at": "2024-01-15T10:45:00Z",
    "completed_at": "2024-01-15T10:46:00Z"
  }
}
```

#### GET /api/export/download/{export_job_id}
**Response (200):**
- Returns the file with appropriate headers
- Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document (for .docx)
- Content-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation (for .pptx)

---

## 6. Error Handling Strategy

### Standard Error Response Format

```json
{
  "status": "error",
  "error_code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": [
    {
      "field": "field_name",
      "error": "field-specific error"
    }
  ],
  "request_id": "req_123456789"
}
```

### HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | OK | Successful GET/POST with response |
| 201 | Created | Resource created successfully |
| 202 | Accepted | Async job queued |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input/schema validation failure |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | User lacks permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Email already exists, duplicate record |
| 422 | Unprocessable Entity | Semantic error (e.g., invalid state transition) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | LLM API down, database unavailable |

### Common Error Codes

- `VALIDATION_ERROR`: Input validation failed
- `AUTHENTICATION_FAILED`: Invalid credentials
- `UNAUTHORIZED_ACCESS`: User lacks permission
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests from user/IP
- `LLM_API_ERROR`: Failure communicating with LLM API
- `GENERATION_TIMEOUT`: Content generation took too long
- `EXPORT_FAILED`: Document export operation failed
- `DATABASE_ERROR`: Database operation failed
- `INVALID_STATE_TRANSITION`: Cannot perform action in current state

---

This completes the comprehensive system design documentation. The document covers architecture, database schema, API specifications, and error handling strategies necessary for implementation.

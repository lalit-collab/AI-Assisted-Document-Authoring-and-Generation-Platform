# AI-Assisted Document Authoring & Generation Platform

## 📋 Executive Overview

A full-stack, production-ready platform that leverages AI (Gemini/OpenAI) to automate professional document and presentation creation. Users define document structures, generate content through intelligent AI prompting, refine through feedback loops, and export to industry-standard formats (.docx, .pptx).

### Key Features
✅ **Smart Authentication**: JWT-based with token refresh  
✅ **Project Management**: Create, organize, and manage multiple projects  
✅ **AI Content Generation**: Powered by Google Gemini or OpenAI GPT-4  
✅ **Interactive Refinement**: Like/dislike/comment feedback system  
✅ **Professional Export**: Word (.docx) and PowerPoint (.pptx) support  
✅ **AI Templates** (Bonus): Auto-generate outlines and slide titles  
✅ **Streaming Generation**: Real-time content generation updates  
✅ **Security First**: Prompt injection prevention, rate limiting, secure key management  

---

## 🏗️ System Architecture

### Technology Stack
| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18 + Redux Toolkit + Tailwind CSS |
| **Backend** | FastAPI (Python 3.9+) + SQLAlchemy |
| **Database** | PostgreSQL with UUID primary keys |
| **LLM** | Google Gemini API / OpenAI GPT-4 |
| **Export** | python-docx, python-pptx |
| **Authentication** | JWT tokens with bcrypt hashing |
| **Deployment** | Docker, AWS/Heroku/Railway |

### High-Level Architecture Flow
```
User (React Frontend)
    ↓
REST API (FastAPI)
    ↓
Service Layer (Business Logic)
    ↓
LLM Integration (Gemini/OpenAI)
    ↓
Database (PostgreSQL)
    ↓
File Export (Word/PowerPoint)
```

### Database Relationships
```
User (1) ──→ (M) Projects ──→ (M) Documents
           ↓
        (M) APIKeys
        
Document (1) ──→ (M) Sections ──→ (M) GeneratedContent ──→ (M) Refinements
```

---

## 📦 Project Structure

```
root/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── core/
│   │   │   ├── config.py           # Environment settings
│   │   │   ├── security.py         # JWT, password hashing
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   └── __init__.py         # SQLAlchemy ORM models
│   │   ├── schemas/
│   │   │   └── __init__.py         # Pydantic request/response schemas
│   │   ├── routes/
│   │   │   ├── auth_routes.py      # Authentication endpoints
│   │   │   ├── project_routes.py   # Project CRUD
│   │   │   ├── document_routes.py  # Document configuration
│   │   │   ├── generation_routes.py# AI generation
│   │   │   ├── refinement_routes.py# Feedback system
│   │   │   ├── export_routes.py    # Export to Word/PowerPoint
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   └── __init__.py         # Business logic services
│   │   ├── database/
│   │   │   └── __init__.py         # DB initialization
│   │   ├── integrations/
│   │   │   └── __init__.py         # LLM client & prompt mgmt
│   │   ├── utils/
│   │   │   ├── export.py           # Export logic
│   │   │   └── __init__.py
│   ├── tests/
│   │   └── test_*.py               # Unit/integration tests
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template
│   ├── docker-compose.yml           # Local development setup
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx       # Authentication
│   │   │   ├── DashboardPage.tsx   # Project list
│   │   │   ├── ProjectCreatePage.tsx
│   │   │   ├── DocumentConfigPage.tsx
│   │   │   ├── GenerationPage.tsx   # AI generation
│   │   │   ├── RefinementPage.tsx   # Feedback interface
│   │   │   └── ExportPage.tsx       # Export options
│   │   ├── components/
│   │   │   ├── OutlineBuilder.tsx
│   │   │   ├── SectionForm.tsx
│   │   │   ├── GenerationMonitor.tsx
│   │   │   ├── RefinementPanel.tsx
│   │   │   └── ExportDialog.tsx
│   │   ├── store/
│   │   │   ├── store.ts             # Redux configuration
│   │   │   ├── slices/
│   │   │   │   ├── authSlice.ts
│   │   │   │   ├── projectSlice.ts
│   │   │   │   └── documentSlice.ts
│   │   ├── utils/
│   │   │   ├── apiClient.ts         # Axios setup
│   │   │   ├── validation.ts
│   │   │   └── formatters.ts
│   │   ├── App.tsx                  # Router setup
│   │   └── main.tsx                 # Entry point
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docs/
│   ├── API.md                       # API documentation
│   ├── DEPLOYMENT.md                # Deployment guide
│   └── ARCHITECTURE.md              # Detailed architecture
└── README.md                         # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Gemini API key or OpenAI API key

### Backend Setup

```bash
# 1. Clone and navigate
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings:
# - DATABASE_URL=postgresql://user:pass@localhost:5432/docgen_db
# - GEMINI_API_KEY=your_key_here
# - SECRET_KEY=your_secret_key

# 5. Initialize database
python -c "from app.database import init_db; init_db()"

# 6. Run server
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment
echo "VITE_API_URL=http://localhost:8000/api" > .env

# 4. Run development server
npm run dev
```

Frontend runs at `http://localhost:5173`

### Docker Compose (Recommended)

```bash
cd backend
docker-compose up -d
```

This sets up:
- PostgreSQL database
- FastAPI backend
- Redis cache (optional)

---

## 🔐 Security Implementation

### Authentication Flow
```
1. User Registration → Hash password with bcrypt
2. Login → Generate JWT access token (30 min) + refresh token (7 days)
3. Token Storage → localStorage (browser) / secure cookies
4. Token Refresh → When access token expires, use refresh token
5. Logout → Clear tokens and cache
```

### Security Features
- ✅ **Prompt Injection Prevention**: Sanitize inputs, add safety guidelines
- ✅ **Rate Limiting**: 100 requests/hour per user
- ✅ **CORS Protection**: Whitelist origins in config
- ✅ **API Key Security**: Encrypted storage, environment variables
- ✅ **Access Control**: Per-user resource isolation
- ✅ **Input Validation**: Pydantic schema validation

### Environment Variables
```env
# .env file (KEEP SECRET)
DATABASE_URL=postgresql://user:password@localhost/docgen_db
SECRET_KEY=generate_with: python -c "import secrets; print(secrets.token_urlsafe(32))"
GEMINI_API_KEY=AIza...
OPENAI_API_KEY=sk-...
LLM_PROVIDER=gemini
DEBUG=False
CORS_ALLOW_CREDENTIALS=True
```

---

## 📡 API Reference

### Authentication
**POST /api/auth/register**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
→ 201 {access_token, refresh_token, user}
```

**POST /api/auth/login**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
→ 200 {access_token, refresh_token, user}
```

### Projects
**POST /api/projects** - Create project
```json
{
  "title": "Q4 Marketing Report",
  "description": "Annual report",
  "document_type": "document"
}
```

**GET /api/projects** - List projects
**GET /api/projects/{project_id}** - Get project
**PUT /api/projects/{project_id}** - Update project
**DELETE /api/projects/{project_id}** - Delete project

### Content Generation
**POST /api/generation/generate** - Generate AI content
```json
{
  "document_id": "uuid",
  "section_id": "uuid",
  "stream": true,
  "prompt_overrides": {"focus": "financial metrics"}
}
→ Streaming or {content_id, content, tokens_used, model_used}
```

### Refinement
**POST /api/refinement/feedback** - Submit feedback
```json
{
  "content_id": "uuid",
  "feedback_type": "dislike",
  "refinement_reason": "too_long",
  "suggested_changes": "Reduce to 200 words"
}
```

### Export
**POST /api/export/generate** - Export document
```json
{
  "document_id": "uuid",
  "export_format": "docx",
  "export_options": {"include_toc": true}
}
→ 202 {export_job_id, status}
```

**GET /api/export/download/{export_job_id}** - Download file

**Bonus: Template Generation**
**POST /api/export/templates/outline** - Generate outline template
**POST /api/export/templates/slide-titles** - Generate slide titles

---

## 🤖 LLM Integration

### Prompt Engineering Strategy

#### 1. Content Generation Prompt Template
```
SAFETY GUIDELINES: [Standards and safeguards]

Generate professional content for the following:
- Section: {section_title}
- Type: {content_type}
- Tone: {tone}
- Length: {length}

Focus Points:
{focus_points}

Content:
```

#### 2. Refinement Prompt Template
```
Original Content:
{original_content}

User Feedback: {feedback_type}
{user_feedback}

Refine the content to:
- Address the feedback
- Maintain professional quality
- Keep original intent

Refined Content:
```

#### 3. Template Generation
```
Generate a {document_type} outline for:
Topic: {topic}
Sections: {num_sections}
Style: {style}

Format as JSON array with {title, description} objects.
```

### Model Selection
- **Gemini**: Faster, cost-effective, good for streaming
- **GPT-4**: More powerful, better for complex tasks

### Token Optimization
- Estimate ~1.3 tokens per word
- Cache prompts for repeated sections
- Stream responses for UX

---

## 📄 Export Implementation

### Word Document (.docx) Export
```python
from docx import Document
from docx.shared import Pt, Inches

doc = Document()
doc.add_heading('Project Title', 0)
doc.add_paragraph('Introduction text')

for section in sections:
    doc.add_heading(section['title'], 1)
    
    for line in section['content'].split('\n'):
        if line.startswith('- '):
            doc.add_paragraph(line[2:], style='List Bullet')
        else:
            doc.add_paragraph(line)
    
    doc.add_page_break()

doc.save('output.docx')
```

### PowerPoint Presentation (.pptx) Export
```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()
title_slide = prs.slides.add_slide(prs.slide_layouts[6])

title_box = title_slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(9), Inches(2))
title_frame = title_box.text_frame
p = title_frame.paragraphs[0]
p.text = "Project Title"
p.font.size = Pt(54)

for section in sections:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    # Add title, content, formatting...

prs.save('output.pptx')
```

---

## ⚙️ Configuration

### Backend Configuration (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db_name
SQLALCHEMY_ECHO=False

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
LLM_PROVIDER=gemini

# Server
DEBUG=False
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600

# Export
EXPORT_TEMP_DIR=./exports
MAX_FILE_SIZE_MB=50
```

### Frontend Configuration (.env)
```env
VITE_API_URL=http://localhost:8000/api
VITE_ENV=development
```

---

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_register_user
```

### Frontend Tests
```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

---

## 📊 Deployment

### Heroku Deployment
```bash
# 1. Create Heroku app
heroku create ai-document-generator

# 2. Set environment variables
heroku config:set DATABASE_URL=postgresql://...
heroku config:set GEMINI_API_KEY=...

# 3. Add Procfile
echo "web: gunicorn app.main:app" > Procfile

# 4. Deploy
git push heroku main
```

### AWS/Railway Deployment
See `DEPLOYMENT.md` for detailed instructions

### Docker Build
```bash
# Build image
docker build -t docgen:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e GEMINI_API_KEY=... \
  docgen:latest
```

---

## 🎯 Bonus Feature: AI-Generated Templates

### Outline Templates
Users can auto-generate document outlines for any topic:
```
POST /api/export/templates/outline
{
  "topic": "Digital Transformation Strategy",
  "document_type": "document",
  "num_sections": 5,
  "style": "professional"
}

Response:
[
  {"title": "Executive Summary", "description": "..."},
  {"title": "Current State Analysis", "description": "..."},
  ...
]
```

### Slide Title Templates
Auto-generate slide titles for presentations:
```
POST /api/export/templates/slide-titles
{
  "topic": "AI in Business",
  "num_slides": 8,
  "audience": "executive"
}

Response: ["Introduction", "Current Trends", ...]
```

---

## 📹 Demo Video Instructions

Create a 5-10 minute demo showcasing:
1. **Login/Registration** (30 sec)
2. **Create Project** (1 min)
3. **Define Document Outline** (1 min)
4. **Generate Content** with streaming (2 min)
5. **Refine with Feedback** (1 min)
6. **Export to Word/PowerPoint** (1 min)

Upload to YouTube or GitHub with unlisted link.

---

## 🔄 Refinement Workflow

### User Feedback Loop
```
1. User views generated content
2. Submits feedback: like | dislike | comment
3. If like → Mark as approved
4. If dislike/comment → Store feedback + regenerate
5. Show new version with improvements
6. Repeat until satisfied
7. Export approved version
```

### Feedback Types
| Type | Action |
|------|--------|
| **Like** | Mark content approved |
| **Dislike** | Ask refinement reason, regenerate |
| **Comment** | Store suggestion, regenerate with context |

---

## 📋 Testing Checklist

- [ ] User registration/login works
- [ ] JWT token refresh works
- [ ] Create project/document
- [ ] Generate content (streaming + non-streaming)
- [ ] Submit feedback and regenerate
- [ ] Export to .docx file
- [ ] Export to .pptx file
- [ ] Rate limiting active
- [ ] CORS headers correct
- [ ] Error handling complete

---

## 📞 Support & Troubleshooting

### Common Issues

**"Connection refused" to database**
- Ensure PostgreSQL running: `brew services start postgresql`
- Check DATABASE_URL in .env

**"API key invalid"**
- Verify GEMINI_API_KEY or OPENAI_API_KEY in .env
- Check API quota and permissions

**"CORS error"**
- Add frontend URL to ALLOWED_ORIGINS in .env
- Frontend and backend must match origins

**"Export fails"**
- Ensure EXPORT_TEMP_DIR exists: `mkdir -p ./exports`
- Check file permissions
- Verify disk space

---

## 📚 Additional Resources

- **API Documentation**: `/api/docs` (Swagger UI)
- **System Design**: See `SYSTEM_DESIGN.md`
- **Deployment Guide**: See `DEPLOYMENT.md`
- **Architecture Details**: See backend `ARCHITECTURE.md`

---




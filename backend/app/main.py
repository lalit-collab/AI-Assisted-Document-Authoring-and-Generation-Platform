"""Main FastAPI Application"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
import logging

from app.core.config import settings
from app.database import init_db
from app.core.security import get_current_user

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.API_VERSION}


# Import and include routers
from app.routes import auth_routes, project_routes, document_routes, generation_routes, refinement_routes, export_routes

app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(project_routes.router, prefix="/api/projects", tags=["Projects"])
app.include_router(document_routes.router, prefix="/api/documents", tags=["Documents"])
app.include_router(generation_routes.router, prefix="/api/generation", tags=["Generation"])
app.include_router(refinement_routes.router, prefix="/api/refinement", tags=["Refinement"])
app.include_router(export_routes.router, prefix="/api/export", tags=["Export"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info"
    )

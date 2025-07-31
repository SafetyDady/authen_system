"""
FastAPI main application.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.db.database import create_tables, db_manager
from app.api.routes import auth, users, admin


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up Authentication System API...")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    # Check database health
    health = db_manager.health_check()
    if health["status"] == "healthy":
        logger.info("Database connection is healthy")
    else:
        logger.error(f"Database connection is unhealthy: {health.get('error')}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Authentication System API...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*"]  # Configure for production
    )


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors,
            "status_code": 422,
            "path": request.url.path,
            "method": request.method
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if settings.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "type": type(exc).__name__,
                "status_code": 500,
                "path": request.url.path,
                "method": request.method
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "status_code": 500,
                "path": request.url.path,
                "method": request.method
            }
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_health = db_manager.health_check()
    
    return {
        "status": "healthy" if db_health["status"] == "healthy" else "unhealthy",
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production",
        "database": db_health,
        "services": {
            "api": "healthy",
            "database": db_health["status"]
        }
    }


# API information endpoint
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs_url": "/docs" if settings.DEBUG else None,
        "health_url": "/health",
        "status": "running"
    }


# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} "
        f"in {process_time:.3f}s"
    )
    
    return response


# Add request ID middleware for tracing
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID for tracing."""
    import uuid
    request_id = str(uuid.uuid4())
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response
import time


if __name__ == "__main__":
    import uvicorn
    import time
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.DEBUG
    )


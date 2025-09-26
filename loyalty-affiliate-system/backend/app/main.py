from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
import uvicorn
import logging

from .core.config import settings
from .core.database import get_db
from .api.v1.api import api_router

# Configure comprehensive logging
import os
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging based on environment
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configure root logger
logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=[
        logging.StreamHandler(),  # Console output
        RotatingFileHandler(
            "logs/app.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
    ]
)

# Create specific loggers
logger = logging.getLogger(__name__)
security_logger = logging.getLogger("security")
audit_logger = logging.getLogger("audit")
performance_logger = logging.getLogger("performance")

# Set specific levels for loggers
security_logger.setLevel(logging.WARNING)
audit_logger.setLevel(logging.INFO)
performance_logger.setLevel(logging.INFO)

# Add security file handler
security_handler = RotatingFileHandler(
    "logs/security.log",
    maxBytes=5*1024*1024,  # 5MB
    backupCount=3
)
security_handler.setFormatter(logging.Formatter(log_format))
security_logger.addHandler(security_handler)

# Add audit file handler
audit_handler = RotatingFileHandler(
    "logs/audit.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=10
)
audit_handler.setFormatter(logging.Formatter(log_format))
audit_logger.addHandler(audit_handler)

# Add performance file handler
perf_handler = RotatingFileHandler(
    "logs/performance.log",
    maxBytes=5*1024*1024,  # 5MB
    backupCount=5
)
perf_handler.setFormatter(logging.Formatter(log_format))
performance_logger.addHandler(perf_handler)

# Create FastAPI application
app = FastAPI(
    title="Loyalty & Affiliate Management System",
    description="A comprehensive loyalty and affiliate management system with WhatsApp integration",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS middleware
# Configure CORS origins based on environment
if settings.ENVIRONMENT == "production":
    # Production: Use configured origins only
    cors_origins = [str(origin).rstrip('/') for origin in settings.BACKEND_CORS_ORIGINS]
    if not cors_origins:
        # Fallback to empty list if no origins configured
        cors_origins = []
else:
    # Development: Allow common development origins
    cors_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080"
    ]

# Add HTTPS variants for production
if settings.ENVIRONMENT == "production":
    https_origins = [origin.replace("http://", "https://") for origin in cors_origins]
    cors_origins.extend(https_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-Forwarded-For",
        "X-Real-IP",
        "User-Agent"
    ],
    expose_headers=["X-Total-Count", "X-Page-Count"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", summary="Health Check", description="Check if the API is running")
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    import time
    start_time = time.time()

    # Basic health check
    health_info = {
        "status": "healthy",
        "message": "Loyalty & Affiliate Management System is running",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }

    # Log health check
    logger.info("Health check performed", extra={"response_time": time.time() - start_time})

    return health_info


@app.get("/health/detailed", summary="Detailed Health Check", description="Comprehensive system health check")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check including database connectivity and external services
    """
    import time
    start_time = time.time()

    health_info = {
        "status": "healthy",
        "checks": {},
        "timestamp": datetime.utcnow().isoformat()
    }

    # Database health check
    try:
        db.execute("SELECT 1")
        health_info["checks"]["database"] = {
            "status": "healthy",
            "response_time": time.time() - start_time
        }
    except Exception as e:
        health_info["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_info["status"] = "degraded"

    # Redis health check (if configured)
    try:
        import redis
        if settings.REDIS_URL != "redis://localhost:6379":
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            health_info["checks"]["redis"] = {"status": "healthy"}
        else:
            health_info["checks"]["redis"] = {"status": "not_configured"}
    except Exception:
        health_info["checks"]["redis"] = {"status": "unhealthy"}

    # External services health check
    external_services = []

    # WhatsApp API health
    if settings.WHATSAPP_ACCESS_TOKEN:
        try:
            response = requests.get(
                f"{settings.WHATSAPP_API_URL}/me",
                headers={"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"},
                timeout=5
            )
            external_services.append({
                "name": "WhatsApp API",
                "status": "healthy" if response.status_code == 200 else "unhealthy"
            })
        except Exception:
            external_services.append({"name": "WhatsApp API", "status": "unhealthy"})

    # ERP API health (if configured)
    if hasattr(settings, 'ERP_HOST') and settings.ERP_HOST:
        try:
            response = requests.get(f"{settings.ERP_HOST}/health", timeout=5)
            external_services.append({
                "name": "ERP System",
                "status": "healthy" if response.status_code == 200 else "unhealthy"
            })
        except Exception:
            external_services.append({"name": "ERP System", "status": "unhealthy"})

    health_info["checks"]["external_services"] = external_services

    # Determine overall status
    if any(check.get("status") == "unhealthy" for check in health_info["checks"].values() if isinstance(check, dict)):
        health_info["status"] = "unhealthy"
    elif any(check.get("status") == "degraded" for check in health_info["checks"].values() if isinstance(check, dict)):
        health_info["status"] = "degraded"

    # Log detailed health check
    logger.info("Detailed health check performed",
                extra={"status": health_info["status"], "response_time": time.time() - start_time})

    return health_info


@app.get("/", summary="Root Endpoint", description="Root endpoint with API information")
async def root():
    """
    Root endpoint providing basic API information
    """
    return {
        "message": "Welcome to Loyalty & Affiliate Management System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
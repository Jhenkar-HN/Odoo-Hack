from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.exceptions import register_exception_handlers
from backend.app.routes.api import api_router
import backend.app.models  # Import all models to ensure metadata registration


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
## Human Resource Management System (HRMS) — Backend & Core Services

**Person 1 Responsibilities**:
* Database architecture & relational models
* Authentication & JWT sessions
* Role-based access control (ADMIN, HR_OFFICER, EMPLOYEE)
* Automatic Login ID generator (`OI + Initials + Year + Seq`)
* Error handling & request validation
* Foundational APIs for Employee, Salary, Attendance, Time-off & Settings modules
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register centralized exception handlers
register_exception_handlers(app)

# Include API routes (both /api for frontend SPA client and /api/v1 for versioned APIs)
app.include_router(api_router, prefix="/api")
app.include_router(api_router, prefix=settings.API_V1_STR)


import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "features", "UI", "static")
if not os.path.exists(STATIC_DIR):
    STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def serve_index():
    if os.path.exists(STATIC_DIR):
        index_file = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


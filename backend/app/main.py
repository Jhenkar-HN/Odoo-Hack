from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.core.exceptions import register_exception_handlers
from backend.app.routes.api import api_router
import backend.app.models  # Import all models to ensure metadata registration


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    yield


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
    lifespan=lifespan,
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

# Include aggregated API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

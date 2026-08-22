import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import employees, stats, uploads, auth, timeoff

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB & Seed Data on Startup
    init_db()
    yield


app = FastAPI(
    title="Human Resource Management System (HRMS) API",
    description="Enterprise HRMS API with Employee CRUD, Role-Based Access (HR vs Employee), Dynamic Salary Computation, Attendance Systray, and Document Management.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(stats.router)
app.include_router(timeoff.router)
app.include_router(uploads.router)

# Mount Static Files
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def serve_index():
    """Serve the Single Page Application index.html."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "HRMS API is running. Build the frontend or visit /docs for interactive Swagger UI."}


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "HRMS Backend API"}

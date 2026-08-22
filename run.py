"""
Unified One-Click Runner for Human Resource Management System (HRMS)
Backend, Database, Authentication, and Modern Glassmorphic SPA Frontend.
"""
import uvicorn
import os
import sys
import subprocess

# Ensure backend package is in pythonpath
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def initialize_database():
    """Apply migrations and seed demo data before starting the local server."""
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=ROOT_DIR, check=True)
    subprocess.run([sys.executable, "-m", "backend.app.utils.seeder"], cwd=ROOT_DIR, check=True)


if __name__ == "__main__":
    initialize_database()
    print("=" * 65)
    print(" [HRMS] Launching Human Resource Management System")
    print(" [*] Web Application URL: http://localhost:8000")
    print(" [*] Swagger API Docs:    http://localhost:8000/docs")
    print(" [*] ReDoc Documentation: http://localhost:8000/redoc")
    print("=" * 65)
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

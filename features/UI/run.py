"""
One-click runner for Human Resource Management System (HRMS)
"""
import uvicorn
import os
import sys

if __name__ == "__main__":
    print("==========================================================")
    print(" [HRMS] Launching Human Resource Management System")
    print(" [*] Application URL: http://localhost:8000")
    print(" [*] Interactive Swagger API Docs: http://localhost:8000/docs")
    print("==========================================================")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

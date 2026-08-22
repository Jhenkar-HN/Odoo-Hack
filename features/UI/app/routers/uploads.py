import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/upload", tags=["Uploads"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    "pdf", "doc", "docx", "png", "jpg", "jpeg", "webp"
}


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """Upload a resume document or avatar image."""
    filename = file.filename or "uploaded_file"
    ext = filename.split(".")[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '.{ext}' is not supported. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Generate safe unique filename
    unique_filename = f"{uuid.uuid4().hex[:10]}_{filename.replace(' ', '_')}"
    target_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_url = f"/static/uploads/{unique_filename}"

    return JSONResponse({
        "success": True,
        "original_filename": filename,
        "filename": unique_filename,
        "url": file_url,
        "file_size": os.path.getsize(target_path)
    })

# File utilities for CV uploads
import os
import uuid
from datetime import datetime
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = "uploads/cvs"
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB

def ensure_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_cv(file: UploadFile) -> tuple:
    """Save CV file, return (original_name, url_path)."""
    ensure_dir()
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
    
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "File too large (max 10MB)")
    
    unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
    path = os.path.join(UPLOAD_DIR, unique_name)
    
    with open(path, "wb") as f:
        f.write(content)
    
    # Use forward slashes for URL compatibility (works on all platforms)
    url_path = f"/uploads/cvs/{unique_name}"
    return file.filename, url_path

def delete_file(path: str):
    """Delete uploaded file."""
    if path and path.startswith("/"):
        path = path[1:]
    # Convert URL-style forward slashes to OS-specific path separators
    if path:
        path = path.replace("/", os.sep)
    if path and os.path.exists(path):
        os.remove(path)

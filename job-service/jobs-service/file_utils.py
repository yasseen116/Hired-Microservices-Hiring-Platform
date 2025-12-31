import os
import uuid
import shutil
from typing import Optional
from fastapi import UploadFile
from pathlib import Path

# Define upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

async def save_upload_file(upload_file: UploadFile) -> Optional[str]:
    """
    Save uploaded file to uploads directory
    Returns the relative path to the saved file or None if failed
    """
    if not upload_file:
        return None
    
    # Check if filename exists
    if not upload_file.filename:
        raise ValueError("No filename provided")
    
    # Get file extension
    file_extension = get_file_extension(upload_file.filename)
    
    # Debug: print the filename and extension
    print(f"Upload file: {upload_file.filename}")
    print(f"File extension: {file_extension}")
    print(f"Allowed extensions: {ALLOWED_EXTENSIONS}")
    
    # Check if file type is allowed
    if not is_allowed_file(upload_file.filename):
        raise ValueError(f"File type '{file_extension}' not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        # Return relative path
        return f"uploads/{unique_filename}"
    except Exception as e:
        print(f"Error saving file: {e}")
        return None
    finally:
        await upload_file.close()

def delete_upload_file(file_path: str) -> bool:
    """
    Delete uploaded file
    Returns True if successful, False otherwise
    """
    try:
        full_path = Path(file_path)
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

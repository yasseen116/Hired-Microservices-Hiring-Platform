# ==============================================================================
# FILE UPLOAD UTILITIES MODULE
# ==============================================================================
# This module handles file uploads for profile photos and CVs.
# It provides functions to:
# 1. Save uploaded files to the server
# 2. Delete files when removed by the user
# 3. Validate file types and sizes
#
# File storage strategy:
# - Files are stored in the 'uploads' directory
# - Photos go in 'uploads/photos/'
# - CVs go in 'uploads/cvs/'
# - Filenames are made unique using timestamps
# ==============================================================================

import os
import uuid
from datetime import datetime
from fastapi import UploadFile, HTTPException

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# These settings control where files are saved and what types are allowed.
# ==============================================================================

# Base directory for all uploads
UPLOAD_DIR = "uploads"

# Subdirectories for different file types
PHOTOS_DIR = os.path.join(UPLOAD_DIR, "photos")
CVS_DIR = os.path.join(UPLOAD_DIR, "cvs")

# Allowed file extensions for photos
ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# Allowed file extensions for CVs
ALLOWED_CV_EXTENSIONS = {".pdf", ".doc", ".docx"}

# Maximum file sizes (in bytes)
MAX_PHOTO_SIZE = 5 * 1024 * 1024   # 5 MB
MAX_CV_SIZE = 10 * 1024 * 1024     # 10 MB


def ensure_directories_exist():
    """
    Creates the upload directories if they don't exist.
    
    This should be called when the application starts to ensure
    the file storage directories are available.
    """
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    os.makedirs(CVS_DIR, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """
    Extracts the file extension from a filename.
    
    Args:
        filename: The original filename (e.g., "photo.jpg")
        
    Returns:
        str: The extension in lowercase (e.g., ".jpg")
    """
    return os.path.splitext(filename)[1].lower()


def generate_unique_filename(original_filename: str) -> str:
    """
    Generates a unique filename to prevent overwrites.
    
    We use a combination of:
    - Timestamp (for sorting)
    - UUID (for uniqueness)
    - Original extension (for file type)
    
    Args:
        original_filename: The original filename from the upload
        
    Returns:
        str: A unique filename like "20231225_abc123.jpg"
    """
    extension = get_file_extension(original_filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}{extension}"


async def save_photo(file: UploadFile) -> str:
    """
    Saves an uploaded photo to the photos directory.
    
    This function:
    1. Validates the file extension
    2. Checks the file size
    3. Saves the file with a unique name
    4. Returns the URL path to the file
    
    Args:
        file: The uploaded file from FastAPI
        
    Returns:
        str: The URL path to access the photo (e.g., "/uploads/photos/abc.jpg")
        
    Raises:
        HTTPException: If file type or size is invalid
    """
    # Ensure directories exist
    ensure_directories_exist()
    
    # Validate file extension
    extension = get_file_extension(file.filename)
    if extension not in ALLOWED_PHOTO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_PHOTO_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > MAX_PHOTO_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_PHOTO_SIZE // (1024*1024)} MB"
        )
    
    # Generate unique filename and save
    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(PHOTOS_DIR, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Return the URL path (not the filesystem path)
    # Use forward slashes for URL compatibility (works on all platforms)
    url_path = f"/uploads/photos/{unique_filename}"
    return url_path


async def save_cv(file: UploadFile) -> tuple:
    """
    Saves an uploaded CV to the CVs directory.
    
    Args:
        file: The uploaded file from FastAPI
        
    Returns:
        tuple: (original_filename, url_path)
        
    Raises:
        HTTPException: If file type or size is invalid
    """
    # Ensure directories exist
    ensure_directories_exist()
    
    # Validate file extension
    extension = get_file_extension(file.filename)
    if extension not in ALLOWED_CV_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_CV_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > MAX_CV_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_CV_SIZE // (1024*1024)} MB"
        )
    
    # Generate unique filename and save
    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(CVS_DIR, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Return both the original name and the URL path
    # Use forward slashes for URL compatibility (works on all platforms)
    url_path = f"/uploads/cvs/{unique_filename}"
    return file.filename, url_path


def delete_file(file_path: str) -> bool:
    """
    Deletes a file from the server.
    
    This function is called when:
    - A user removes their profile photo
    - A user removes their CV
    - A user uploads a new file to replace the old one
    
    Args:
        file_path: The URL path to the file (e.g., "/uploads/photos/abc.jpg")
        
    Returns:
        bool: True if file was deleted, False if it didn't exist
    """
    # Remove leading slash to get filesystem path
    if file_path.startswith("/"):
        file_path = file_path[1:]
    
    # Convert URL-style forward slashes to OS-specific path separators
    file_path = file_path.replace("/", os.sep)

    # Check if file exists and delete
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    
    return False

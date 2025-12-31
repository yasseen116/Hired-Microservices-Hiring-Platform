# ==============================================================================
# API ROUTES MODULE
# ==============================================================================
# This module defines all the HTTP endpoints for the authentication service.
# It handles user registration, login, profile management, and file uploads.
#
# ENDPOINT OVERVIEW:
# 
# Authentication (Public):
# - POST /api/auth/signup     - Register a new user
# - POST /api/auth/login      - Login and get JWT token
# - GET  /api/auth/verify     - Verify a token (for other services)
#
# User Profile (Protected - requires JWT):
# - GET  /api/auth/me         - Get current user's data
# - PUT  /api/auth/profile    - Update profile fields
# - POST /api/auth/profile/photo   - Upload profile photo
# - DELETE /api/auth/profile/photo - Remove profile photo
# - POST /api/auth/profile/cv      - Upload CV file
# - DELETE /api/auth/profile/cv    - Remove CV file
# ==============================================================================

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import json

# Import our custom modules
from database import get_db
from models import User
from schemas import (
    UserSignup, 
    UserLogin, 
    UserResponse, 
    ProfileUpdate, 
    TokenResponse,
    TokenVerifyResponse,
    MessageResponse,
    ApplicantResponse
)
from auth_utils import (
    hash_password, 
    verify_password, 
    create_access_token, 
    decode_token,
    get_current_user,
    security
)
from file_utils import save_photo, save_cv, delete_file

# ==============================================================================
# ROUTER SETUP
# ==============================================================================
# APIRouter is used to organize routes into groups.
# - prefix: All routes in this router will start with /api/auth
# - tags: Groups routes in the Swagger documentation
# ==============================================================================
router = APIRouter(prefix="/api/auth", tags=["authentication"])


# ==============================================================================
# USER SIGNUP ENDPOINT
# ==============================================================================
# POST /api/auth/signup
# 
# Creates a new user account with minimal required information:
# - email (must be unique)
# - password (will be hashed)
# - name
#
# Returns a JWT token so the user is immediately logged in after signup.
# ==============================================================================

@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    This endpoint:
    1. Validates that the email is not already registered
    2. Hashes the password for secure storage
    3. Creates the user in the database
    4. Returns a JWT token for immediate authentication
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "securepassword",
            "name": "John Doe"
        }
    
    Returns:
        TokenResponse with access_token and user data
        
    Raises:
        400: Email already registered
    """
    # ==========================================================================
    # Check if email is already registered
    # ==========================================================================
    # We need to prevent duplicate accounts with the same email
    # This query checks if any user exists with this email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists. Please log in or use a different email."
        )
    
    # ==========================================================================
    # Create the new user
    # ==========================================================================
    # Hash the password before storing - NEVER store plain text passwords!
    hashed_password = hash_password(user_data.password)
    
    # Create a new User object with the provided data
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name,
        role=user_data.role,
        company_name=user_data.company_name if user_data.role == "provider" else None
    )
    
    # Add the user to the database session
    db.add(new_user)
    
    # Commit the transaction to save the user
    db.commit()
    
    # Refresh to get the auto-generated ID
    db.refresh(new_user)
    
    # ==========================================================================
    # Generate JWT token for immediate authentication
    # ==========================================================================
    # This allows the frontend to immediately start making authenticated requests
    access_token = create_access_token(new_user.id, new_user.email)
    
    # ==========================================================================
    # Return the token and user data
    # ==========================================================================
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**new_user.to_dict())
    )


# ==============================================================================
# USER LOGIN ENDPOINT
# ==============================================================================
# POST /api/auth/login
#
# Authenticates a user with email and password.
# Returns a JWT token if credentials are valid.
# ==============================================================================

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT token.
    
    This endpoint:
    1. Finds the user by email
    2. Verifies the password against the stored hash
    3. Returns a JWT token if credentials are valid
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "userpassword"
        }
    
    Returns:
        TokenResponse with access_token and user data
        
    Raises:
        401: Invalid email or password
    """
    # ==========================================================================
    # Find the user by email
    # ==========================================================================
    user = db.query(User).filter(User.email == login_data.email).first()
    
    # ==========================================================================
    # Verify credentials
    # ==========================================================================
    # We use a generic error message for security
    # This prevents attackers from knowing if an email is registered
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )
    
    # Verify the password against the stored hash
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )
    
    # ==========================================================================
    # Generate and return JWT token
    # ==========================================================================
    access_token = create_access_token(user.id, user.email)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user.to_dict())
    )


# ==============================================================================
# GET CURRENT USER ENDPOINT
# ==============================================================================
# GET /api/auth/me
#
# Returns the currently authenticated user's data.
# Requires a valid JWT token in the Authorization header.
# ==============================================================================

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the currently authenticated user's profile.
    
    This is a PROTECTED endpoint - requires a valid JWT token.
    The token must be provided in the Authorization header:
    Authorization: Bearer <your_token>
    
    The get_current_user dependency:
    1. Extracts the token from the header
    2. Verifies it's valid and not expired
    3. Returns the user object
    
    Returns:
        UserResponse with all user profile data (except password)
    """
    # The current_user is injected by the get_current_user dependency
    # If we reach here, the user is authenticated
    return UserResponse(**current_user.to_dict())


# ==============================================================================
# APPLICANT LOOKUP (PROVIDER ONLY)
# ==============================================================================

@router.get("/users/{user_id}", response_model=ApplicantResponse)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "provider" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this user.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user_data = user.to_dict()
    return ApplicantResponse(
        id=user_data.get("id"),
        name=user_data.get("name"),
        email=user_data.get("email"),
        jobTitle=user_data.get("jobTitle"),
        phone=user_data.get("phone"),
        location=user_data.get("location"),
        photo=user_data.get("photo")
    )


# ==============================================================================
# UPDATE PROFILE ENDPOINT
# ==============================================================================
# PUT /api/auth/profile
#
# Updates the user's profile fields (excluding auth fields like email/password).
# Only provided fields are updated - omitted fields remain unchanged.
# ==============================================================================

@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's profile.
    
    This endpoint:
    1. Takes a ProfileUpdate with any combination of profile fields
    2. Updates only the fields that were provided
    3. Returns the updated user data
    
    Request Body (all fields optional):
        {
            "job_title": "Senior Developer",
            "skills": ["Python", "FastAPI"],
            "phone": "+1234567890",
            "location": "New York, USA",
            "about": "I'm a passionate developer...",
            "experience": [
                {"role": "Developer", "company": "TechCorp", "years": "2020-2023"}
            ],
            "education": [
                {"degree": "BSc CS", "university": "MIT", "year": "2020"}
            ]
        }
    
    Returns:
        Updated UserResponse
    """
    # ==========================================================================
    # Extract only the fields that were provided (not None)
    # ==========================================================================
    # model_dump(exclude_unset=True) returns only fields explicitly set in request
    update_data = profile_data.model_dump(exclude_unset=True)
    
    # ==========================================================================
    # Update each provided field
    # ==========================================================================
    for field, value in update_data.items():
        # Handle JSON fields (skills, experience, education)
        # These need to be converted to JSON strings for storage
        if field in ["skills", "experience", "education"]:
            if value is not None:
                # Convert list/dict to JSON string
                setattr(current_user, field, json.dumps(value))
        else:
            # For simple fields, set directly
            setattr(current_user, field, value)
    
    # ==========================================================================
    # Save changes to database
    # ==========================================================================
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(**current_user.to_dict())


# ==============================================================================
# UPLOAD PROFILE PHOTO ENDPOINT
# ==============================================================================
# POST /api/auth/profile/photo
#
# Uploads a new profile photo for the current user.
# Automatically deletes the old photo if one exists.
# ==============================================================================

@router.post("/profile/photo", response_model=UserResponse)
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a profile photo for the current user.
    
    This endpoint:
    1. Validates the file type (jpg, png, gif, webp)
    2. Validates the file size (max 5MB)
    3. Saves the file with a unique name
    4. Updates the user's photo URL
    5. Deletes the old photo if one existed
    
    Request:
        Content-Type: multipart/form-data
        file: The image file
        
    Returns:
        Updated UserResponse with new photo URL
    """
    # ==========================================================================
    # Delete old photo if exists
    # ==========================================================================
    if current_user.photo:
        delete_file(current_user.photo)
    
    # ==========================================================================
    # Save the new photo
    # ==========================================================================
    # save_photo handles validation and returns the URL path
    photo_url = await save_photo(file)
    
    # ==========================================================================
    # Update user record
    # ==========================================================================
    current_user.photo = photo_url
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(**current_user.to_dict())


# ==============================================================================
# DELETE PROFILE PHOTO ENDPOINT
# ==============================================================================
# DELETE /api/auth/profile/photo
#
# Removes the current user's profile photo.
# ==============================================================================

@router.delete("/profile/photo", response_model=MessageResponse)
def delete_photo(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove the current user's profile photo.
    
    This endpoint:
    1. Checks if a photo exists
    2. Deletes the file from storage
    3. Clears the photo URL in the database
    
    Returns:
        MessageResponse confirming deletion
    """
    # Check if photo exists
    if not current_user.photo:
        raise HTTPException(
            status_code=404,
            detail="No profile photo to delete."
        )
    
    # Delete the file from storage
    delete_file(current_user.photo)
    
    # Clear the photo URL in database
    current_user.photo = None
    db.commit()
    
    return MessageResponse(message="Profile photo removed successfully.")


# ==============================================================================
# UPLOAD CV ENDPOINT
# ==============================================================================
# POST /api/auth/profile/cv
#
# Uploads a CV/resume file for the current user.
# ==============================================================================

@router.post("/profile/cv", response_model=UserResponse)
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a CV/resume for the current user.
    
    This endpoint:
    1. Validates the file type (pdf, doc, docx)
    2. Validates the file size (max 10MB)
    3. Saves the file with a unique name
    4. Updates the user's CV information
    5. Deletes the old CV if one existed
    
    Request:
        Content-Type: multipart/form-data
        file: The CV file
        
    Returns:
        Updated UserResponse with CV info
    """
    # Delete old CV if exists
    if current_user.cv_url:
        delete_file(current_user.cv_url)
    
    # Save the new CV (returns tuple of original name and URL)
    cv_name, cv_url = await save_cv(file)
    
    # Update user record
    current_user.cv_name = cv_name
    current_user.cv_url = cv_url
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(**current_user.to_dict())


# ==============================================================================
# DELETE CV ENDPOINT
# ==============================================================================
# DELETE /api/auth/profile/cv
#
# Removes the current user's CV file.
# ==============================================================================

@router.delete("/profile/cv", response_model=MessageResponse)
def delete_cv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove the current user's CV.
    
    Returns:
        MessageResponse confirming deletion
    """
    # Check if CV exists
    if not current_user.cv_url:
        raise HTTPException(
            status_code=404,
            detail="No CV to delete."
        )
    
    # Delete the file from storage
    delete_file(current_user.cv_url)
    
    # Clear CV info in database
    current_user.cv_name = None
    current_user.cv_url = None
    db.commit()
    
    return MessageResponse(message="CV removed successfully.")


# ==============================================================================
# TOKEN VERIFICATION ENDPOINT
# ==============================================================================
# GET /api/auth/verify
#
# This endpoint is used by OTHER microservices to verify tokens.
# When the Job Service receives a request, it can call this endpoint
# to check if the token is valid and get the user's ID.
# ==============================================================================

@router.get("/verify", response_model=TokenVerifyResponse)
def verify_token(current_user: User = Depends(get_current_user)):
    """
    Verify the current token and return user information.
    
    This endpoint is designed to be called by OTHER microservices
    to verify that a token is valid. For example:
    
    1. User makes request to Job Service with token
    2. Job Service calls Auth Service: GET /api/auth/verify
       with the same Authorization header
    3. Auth Service returns { valid: true, user_id: 123 }
    4. Job Service knows the request is authenticated
    
    Returns:
        TokenVerifyResponse with validity status and user info
    """
    # If we reach here, the token is valid (get_current_user would have raised)
    return TokenVerifyResponse(
        valid=True,
        user_id=current_user.id,
        email=current_user.email
    )

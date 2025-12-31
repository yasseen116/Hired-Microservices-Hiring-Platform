# ==============================================================================
# PYDANTIC SCHEMAS MODULE
# ==============================================================================
# This module defines Pydantic models (schemas) for request/response validation.
# Pydantic is a data validation library that uses Python type hints to:
# 1. Validate incoming request data
# 2. Convert data between types automatically
# 3. Generate automatic API documentation
#
# These schemas are DIFFERENT from SQLAlchemy models:
# - SQLAlchemy models = Database structure (how data is stored)
# - Pydantic schemas = API structure (how data is sent/received)
# ==============================================================================

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# ==============================================================================
# AUTHENTICATION SCHEMAS (Signup & Login)
# ==============================================================================
# These schemas handle user registration and login requests.
# They only include the minimum required fields for authentication.
# ==============================================================================

class UserSignup(BaseModel):
    """
    Schema for user registration requests.
    
    This is intentionally minimal - only the essential fields needed to
    create an account. All other profile information is added later via
    the /api/auth/profile endpoint.
    
    Attributes:
        email: User's email address (used for login)
        password: Plain text password (will be hashed before storage)
        name: User's display name
    
    Example request body:
    {
        "email": "john@example.com",
        "password": "securepass123",
        "name": "John Doe"
    }
    """
    # EmailStr is a special Pydantic type that validates email format
    email: EmailStr = Field(
        ...,  # ... means required (no default value)
        description="User's email address for login",
        examples=["john@example.com"]
    )
    
    # Password validation: minimum 6 characters
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Password (minimum 6 characters)"
    )
    
    # User's full name
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User's full name"
    )
    
    # User role: seeker or provider
    role: str = Field(
        default="seeker",
        description="User role: 'seeker' or 'provider'"
    )
    
    # Company name (required for providers)
    company_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Company name (only for providers)"
    )


class UserLogin(BaseModel):
    """
    Schema for user login requests.
    
    Attributes:
        email: Registered email address
        password: User's password
    
    Example request body:
    {
        "email": "john@example.com",
        "password": "securepass123"
    }
    """
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="User's password")


# ==============================================================================
# PROFILE SCHEMAS (Profile Updates)
# ==============================================================================
# These schemas handle profile update requests.
# All fields are optional - users only send the fields they want to change.
# ==============================================================================

class ExperienceItem(BaseModel):
    """
    Schema for a single work experience entry.
    
    Example:
    {
        "role": "Software Engineer",
        "company": "Google",
        "years": "2020-2023"
    }
    """
    role: str = Field(..., description="Job title/role")
    company: str = Field(..., description="Company name")
    years: str = Field(..., description="Duration (e.g., '2020-2023')")


class EducationItem(BaseModel):
    """
    Schema for a single education entry.
    
    Example:
    {
        "degree": "BSc Computer Science",
        "university": "MIT",
        "year": "2020"
    }
    """
    degree: str = Field(..., description="Degree name")
    university: str = Field(..., description="University/institution name")
    year: str = Field(..., description="Graduation year")


class ProfileUpdate(BaseModel):
    """
    Schema for profile update requests.
    
    ALL fields are optional - users only send what they want to change.
    This follows the "partial update" pattern common in REST APIs.
    
    Example request body (updating just skills and job title):
    {
        "job_title": "Senior Developer",
        "skills": ["Python", "FastAPI", "React"]
    }
    """
    # Job/Career information
    job_title: Optional[str] = Field(None, max_length=255, description="Current job title")
    skills: Optional[List[str]] = Field(None, description="List of skills")
    
    # Contact information
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    location: Optional[str] = Field(None, max_length=255, description="Location/city")
    
    # Bio section
    about: Optional[str] = Field(None, description="About me text")
    
    # Work history and education
    experience: Optional[List[ExperienceItem]] = Field(None, description="Work experience list")
    education: Optional[List[EducationItem]] = Field(None, description="Education history")


# ==============================================================================
# RESPONSE SCHEMAS
# ==============================================================================
# These schemas define the structure of API responses.
# They ensure consistent response format and exclude sensitive data.
# ==============================================================================

class UserResponse(BaseModel):
    """
    Schema for user data in API responses.
    
    Note: This NEVER includes the password or password_hash.
    All sensitive data is excluded from API responses.
    
    The Config class with from_attributes=True allows this schema
    to be created directly from SQLAlchemy model instances.
    """
    id: int
    email: str
    name: str
    role: str = "seeker"
    companyName: Optional[str] = None
    
    # Profile fields (may be null for new users)
    jobTitle: Optional[str] = None
    skills: Optional[List[str]] = None
    cvName: Optional[str] = None
    cvUrl: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    about: Optional[str] = None
    photo: Optional[str] = None
    experience: Optional[List[dict]] = None
    education: Optional[List[dict]] = None
    
    # Timestamps
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    class Config:
        """
        Pydantic configuration for this schema.
        
        from_attributes=True (formerly orm_mode=True):
        - Allows Pydantic to read data from SQLAlchemy model attributes
        - Without this, you'd need to convert the model to a dict first
        """
        from_attributes = True


class ApplicantResponse(BaseModel):
    """
    Limited user data for providers reviewing applicants.
    """
    id: int
    name: str
    email: str
    jobTitle: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    photo: Optional[str] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """
    Schema for login/signup responses that include a JWT token.
    
    The response includes:
    1. access_token: The JWT token string
    2. token_type: Always "bearer" (OAuth2 standard)
    3. user: The user's public profile data
    
    Example response:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": "john@example.com",
            "name": "John Doe",
            ...
        }
    }
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    user: UserResponse = Field(..., description="User profile data")


class TokenVerifyResponse(BaseModel):
    """
    Schema for token verification responses.
    
    Used by other microservices to verify if a token is valid
    and get the associated user ID.
    
    Example response:
    {
        "valid": true,
        "user_id": 123,
        "email": "john@example.com"
    }
    """
    valid: bool = Field(..., description="Whether the token is valid")
    user_id: Optional[int] = Field(None, description="User ID if token is valid")
    email: Optional[str] = Field(None, description="User email if token is valid")


class MessageResponse(BaseModel):
    """
    Simple message response schema for operations like delete.
    
    Example response:
    {
        "message": "Photo removed successfully"
    }
    """
    message: str

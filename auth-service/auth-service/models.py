# ==============================================================================
# USER MODEL MODULE
# ==============================================================================
# This module defines the User database model using SQLAlchemy ORM.
# The User model represents the 'users' table in our SQLite database.
#
# Each attribute of the class corresponds to a column in the database table.
# SQLAlchemy handles the conversion between Python objects and database rows.
# ==============================================================================

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base
import json

# ==============================================================================
# USER MODEL CLASS
# ==============================================================================
# This class defines the structure of the 'users' table in the database.
# It inherits from Base (defined in database.py) which provides:
# - Automatic table creation based on class attributes
# - Methods for querying, inserting, updating, and deleting records
# ==============================================================================
class User(Base):
    """
    Database model representing a user in the Hired platform.
    
    This model stores:
    - Authentication info (email, password_hash)
    - Basic profile info (name)
    - Extended profile info (job_title, skills, etc.)
    - File references (cv_name, cv_url, photo)
    - Timestamps for auditing
    """
    
    # ==========================================================================
    # TABLE NAME
    # ==========================================================================
    # The __tablename__ attribute tells SQLAlchemy what to name the table
    # in the database. This is required for all models.
    # ==========================================================================
    __tablename__ = "users"
    
    # ==========================================================================
    # PRIMARY KEY & AUTHENTICATION FIELDS
    # ==========================================================================
    # These are the core fields required for user authentication.
    # The password is NEVER stored in plain text - only the hash is stored.
    # ==========================================================================
    
    # Unique identifier for each user, auto-incremented by the database
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Email is used for login, must be unique across all users
    # index=True creates a database index for faster lookups
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # Password hash - NEVER store plain text passwords!
    # We use bcrypt to create a secure, one-way hash of the password
    password_hash = Column(String(255), nullable=False)
    
    # User's display name (required at signup)
    name = Column(String(255), nullable=False)
    
    # User role: "seeker" (looking for jobs) or "provider" (posting jobs)
    role = Column(String(50), nullable=False, default="seeker")
    
    # Company name (only for providers)
    company_name = Column(String(255), nullable=True)
    
    # ==========================================================================
    # PROFILE FIELDS (Updated via /api/auth/profile endpoint)
    # ==========================================================================
    # These fields are optional and can be updated after signup.
    # They are not required during initial registration.
    # ==========================================================================
    
    # User's current job title or desired position
    job_title = Column(String(255), nullable=True)
    
    # Skills are stored as a JSON array string, e.g., '["Python", "FastAPI"]'
    # We use Text type to allow for longer skill lists
    skills = Column(Text, nullable=True)  # JSON array stored as string
    
    # CV/Resume file information
    cv_name = Column(String(255), nullable=True)  # Original filename
    cv_url = Column(String(500), nullable=True)   # Path to stored file
    
    # Contact information
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Bio/About section for the profile
    about = Column(Text, nullable=True)
    
    # Profile photo URL
    photo = Column(String(500), nullable=True)
    
    # Work experience stored as JSON array
    # Format: [{"role": "Dev", "company": "ABC", "years": "2020-2022"}, ...]
    experience = Column(Text, nullable=True)
    
    # Education history stored as JSON array
    # Format: [{"degree": "BSc", "university": "MIT", "year": "2020"}, ...]
    education = Column(Text, nullable=True)
    
    # ==========================================================================
    # TIMESTAMP FIELDS
    # ==========================================================================
    # These fields automatically track when records are created and modified.
    # server_default=func.now() sets the value automatically on INSERT
    # onupdate=func.now() updates the value automatically on UPDATE
    # ==========================================================================
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================
    
    def to_dict(self):
        """
        Converts the User model to a dictionary for API responses.
        
        This method:
        1. Converts all fields to a dictionary
        2. Parses JSON string fields (skills, experience, education) back to lists
        3. Excludes sensitive data (password_hash)
        4. Formats datetime objects to ISO strings
        
        Returns:
            dict: User data suitable for JSON serialization
        """
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "companyName": self.company_name,
            
            # Profile information
            "jobTitle": self.job_title,
            
            # Parse JSON strings back to Python lists/arrays
            # The 'or "[]"' handles cases where the field is None
            "skills": json.loads(self.skills) if self.skills else [],
            
            # File references
            "cvName": self.cv_name,
            "cvUrl": self.cv_url,
            
            # Contact info
            "phone": self.phone,
            "location": self.location,
            "about": self.about,
            "photo": self.photo,
            
            # Complex profile data (JSON arrays)
            "experience": json.loads(self.experience) if self.experience else [],
            "education": json.loads(self.education) if self.education else [],
            
            # Timestamps formatted as ISO strings for JavaScript compatibility
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }

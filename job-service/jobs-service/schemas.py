from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class JobBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., min_length=1, max_length=255)
    experience: str = Field(..., min_length=1, max_length=100)
    salary: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., min_length=1, max_length=50)  # On-site, Hybrid, Remote
    category: str = Field(..., min_length=1, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)
    description: List[str] = Field(..., min_items=1)
    responsibilities: List[str] = Field(..., min_items=1)
    soft_skills: List[str] = Field(..., min_items=1)
    qualifications: List[str] = Field(..., min_items=1)

class JobCreate(JobBase):
    """Schema for creating a new job"""
    pass

class JobUpdate(BaseModel):
    """Schema for updating a job - all fields are optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    experience: Optional[str] = Field(None, min_length=1, max_length=100)
    salary: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)
    description: Optional[List[str]] = Field(None, min_items=1)
    responsibilities: Optional[List[str]] = Field(None, min_items=1)
    soft_skills: Optional[List[str]] = Field(None, min_items=1)
    qualifications: Optional[List[str]] = Field(None, min_items=1)

class JobResponse(JobBase):
    """Schema for job responses"""
    id: int
    logoUrl: Optional[str] = None
    softSkills: List[str]
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class JobListItem(BaseModel):
    """Simplified schema for job listings"""
    id: int
    title: str
    company: str
    location: str
    experience: str
    salary: str
    type: str
    category: str
    logoUrl: Optional[str] = None
    
    class Config:
        from_attributes = True

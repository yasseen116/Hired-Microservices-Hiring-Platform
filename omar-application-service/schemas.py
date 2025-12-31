from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ApplicationCreate(BaseModel):
    """For JSON body requests (without file upload)."""
    job_id: int
    cover_letter: Optional[str] = None

class ApplicationUpdate(BaseModel):
    """For updating application status."""
    status: str  # pending, accepted, rejected

class ApplicationResponse(BaseModel):
    id: int
    userId: int
    jobId: int
    status: str
    cvName: Optional[str] = None
    cvUrl: Optional[str] = None
    coverLetter: Optional[str] = None
    appliedAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    # Enriched from job service
    jobTitle: Optional[str] = None
    company: Optional[str] = None
    # Enriched from auth service (for providers reviewing applicants)
    applicantName: Optional[str] = None
    applicantEmail: Optional[str] = None
    applicantPhone: Optional[str] = None
    applicantLocation: Optional[str] = None
    applicantPhoto: Optional[str] = None
    applicantJobTitle: Optional[str] = None

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    message: str

class CheckAppliedResponse(BaseModel):
    applied: bool
    applicationId: Optional[int] = None
    status: Optional[str] = None

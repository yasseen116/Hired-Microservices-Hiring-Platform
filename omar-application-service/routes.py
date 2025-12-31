from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import requests

import models, schemas, database
from auth_utils import get_current_user_id
from file_utils import save_cv, delete_file

router = APIRouter()

JOB_SERVICE_URL = "http://localhost:8000"
AUTH_SERVICE_URL = "http://localhost:8002"

def get_job_details(job_id: int) -> dict:
    """Fetch job details from job service."""
    try:
        response = requests.get(f"{JOB_SERVICE_URL}/api/jobs/{job_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return None

def get_applicant_details(user_id: int, auth_header: Optional[str]) -> Optional[dict]:
    if not auth_header:
        return None
    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/api/auth/users/{user_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return None


def enrich_application(app: models.Application, auth_header: Optional[str] = None, include_applicant: bool = False) -> dict:
    """Add job title/company and optional applicant data to response."""
    data = app.to_dict()
    job = get_job_details(app.job_id)
    if job:
        data["jobTitle"] = job.get("title")
        data["company"] = job.get("company")
    if include_applicant:
        applicant = get_applicant_details(app.user_id, auth_header)
        if applicant:
            data["applicantName"] = applicant.get("name")
            data["applicantEmail"] = applicant.get("email")
            data["applicantPhone"] = applicant.get("phone")
            data["applicantLocation"] = applicant.get("location")
            data["applicantPhoto"] = applicant.get("photo")
            data["applicantJobTitle"] = applicant.get("jobTitle")
    return data


@router.post("/", response_model=schemas.ApplicationResponse, status_code=201)
async def apply_for_job(
    job_id: int = Form(...),
    cover_letter: Optional[str] = Form(None),
    cv: Optional[UploadFile] = File(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Submit a job application (requires authentication)."""
    # Check for duplicate
    existing = db.query(models.Application).filter(
        models.Application.user_id == user_id,
        models.Application.job_id == job_id
    ).first()
    if existing:
        raise HTTPException(400, "You have already applied to this job")
    
    # Verify job exists
    job = get_job_details(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    
    # Handle CV upload
    cv_name, cv_url = None, None
    if cv:
        cv_name, cv_url = await save_cv(cv)
    
    # Create application
    new_app = models.Application(
        user_id=user_id,
        job_id=job_id,
        status="pending",
        cover_letter=cover_letter,
        cv_name=cv_name,
        cv_url=cv_url
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    
    return enrich_application(new_app)


@router.get("/my", response_model=List[schemas.ApplicationResponse])
def get_my_applications(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Get current user's applications."""
    apps = db.query(models.Application).filter(
        models.Application.user_id == user_id
    ).order_by(models.Application.applied_at.desc()).all()
    
    return [enrich_application(app) for app in apps]


@router.get("/check/{job_id}", response_model=schemas.CheckAppliedResponse)
def check_if_applied(
    job_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Check if user already applied to a job."""
    existing = db.query(models.Application).filter(
        models.Application.user_id == user_id,
        models.Application.job_id == job_id
    ).first()
    
    return {
        "applied": existing is not None,
        "applicationId": existing.id if existing else None,
        "status": existing.status if existing else None
    }


@router.get("/{app_id}", response_model=schemas.ApplicationResponse)
def get_application(
    app_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Get a specific application."""
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(404, "Application not found")
    if app.user_id != user_id:
        raise HTTPException(403, "Not authorized")
    
    return enrich_application(app)


@router.get("/job/{job_id}", response_model=List[schemas.ApplicationResponse])
def get_applications_for_job(
    job_id: int,
    authorization: Optional[str] = Header(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Get all applications for a job (for employers)."""
    apps = db.query(models.Application).filter(
        models.Application.job_id == job_id
    ).order_by(models.Application.applied_at.desc()).all()
    
    return [enrich_application(app, auth_header=authorization, include_applicant=True) for app in apps]


@router.put("/{app_id}/status", response_model=schemas.ApplicationResponse)
def update_status(
    app_id: int,
    update: schemas.ApplicationUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Update application status (for employers)."""
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(404, "Application not found")
    
    app.status = update.status
    db.commit()
    db.refresh(app)
    
    return enrich_application(app)


@router.delete("/{app_id}", response_model=schemas.MessageResponse)
def withdraw_application(
    app_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Withdraw/delete an application."""
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(404, "Application not found")
    if app.user_id != user_id:
        raise HTTPException(403, "Not authorized")
    
    # Delete CV file if exists
    if app.cv_url:
        delete_file(app.cv_url)
    
    db.delete(app)
    db.commit()
    
    return {"message": "Application withdrawn successfully"}

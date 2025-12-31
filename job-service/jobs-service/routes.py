from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from database import get_db
from models import Job
from schemas import JobCreate, JobUpdate, JobResponse, JobListItem
from file_utils import save_upload_file, delete_upload_file

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.get("/", response_model=List[JobListItem])
def get_jobs(
    type: Optional[str] = Query(None, description="Filter by job type (On-site, Hybrid, Remote)"),
    city: Optional[str] = Query(None, description="Filter by city/location"),
    category: Optional[str] = Query(None, description="Filter by job category"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get all jobs with optional filtering and pagination
    """
    query = db.query(Job)
    
    # Apply filters
    if type:
        query = query.filter(Job.type == type)
    if city:
        query = query.filter(Job.location.contains(city))
    if category:
        query = query.filter(Job.category == category)
    
    # Get jobs with pagination
    jobs = query.offset(skip).limit(limit).all()
    
    # Convert to response format
    result = []
    for job in jobs:
        result.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "experience": job.experience,
            "salary": job.salary,
            "type": job.type,
            "category": job.category,
            "logoUrl": job.logo_url
        })
    
    return result

@router.get("/{job_id}", response_model=dict)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """
    Get a specific job by ID with full details
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job.to_dict()

@router.get("/{job_id}/similar", response_model=List[JobListItem])
def get_similar_jobs(
    job_id: int, 
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """
    Get similar jobs based on category (excluding the current job)
    """
    # Get the current job to find its category
    current_job = db.query(Job).filter(Job.id == job_id).first()
    
    if not current_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Find similar jobs in the same category
    similar_jobs = db.query(Job).filter(
        Job.category == current_job.category,
        Job.id != job_id
    ).limit(limit).all()
    
    # Convert to response format
    result = []
    for job in similar_jobs:
        result.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "experience": job.experience,
            "salary": job.salary,
            "type": job.type,
            "category": job.category,
            "logoUrl": job.logo_url
        })
    
    return result

@router.post("/", response_model=dict, status_code=201)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """
    Create a new job posting (JSON body)
    """
    # Convert lists to JSON strings for storage
    new_job = Job(
        title=job.title,
        company=job.company,
        location=job.location,
        experience=job.experience,
        salary=job.salary,
        type=job.type,
        category=job.category,
        logo_url=job.logo_url,
        description=json.dumps(job.description),
        responsibilities=json.dumps(job.responsibilities),
        soft_skills=json.dumps(job.soft_skills),
        qualifications=json.dumps(job.qualifications)
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    return new_job.to_dict()

@router.post("/with-logo", response_model=dict, status_code=201)
async def create_job_with_logo(
    title: str = Form(...),
    company: str = Form(...),
    location: str = Form(...),
    experience: str = Form(...),
    salary: str = Form(...),
    type: str = Form(...),
    category: str = Form(...),
    # Changed from str to List[str] to capture ALL form values, not just the last one
    # When HTML forms send multiple inputs with the same name, FastAPI needs List[str]
    description: List[str] = Form(...),
    responsibilities: List[str] = Form(...),
    soft_skills: List[str] = Form(...),
    qualifications: List[str] = Form(...),
    logo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Create a new job posting with logo upload (multipart/form-data)
    
    List fields (description, responsibilities, soft_skills, qualifications) can be sent as:
    1. Multiple form fields with the same name (e.g., soft_skills=Python&soft_skills=FastAPI)
    2. A single JSON array string (e.g., soft_skills=["Python","FastAPI"])
    """
    def parse_list_field(field_name: str, values: List[str]) -> List[str]:
        """
        Handles list fields that might come as:
        - Multiple separate form values: ["Python", "FastAPI"]
        - A single JSON string: ['["Python", "FastAPI"]']
        
        Returns a flat list of strings.
        """
        # If we received multiple values, use them directly
        if len(values) > 1:
            # Filter out empty strings
            return [v.strip() for v in values if v.strip()]
        
        # If we received a single value, check if it's a JSON array
        if len(values) == 1:
            single_value = values[0]
            
            # Try to parse as JSON (in case frontend sent a JSON array string)
            try:
                parsed = json.loads(single_value)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
                if isinstance(parsed, str):
                    return [parsed.strip()] if parsed.strip() else []
            except json.JSONDecodeError:
                # Not JSON, treat as plain text
                stripped = single_value.strip()
                return [stripped] if stripped else []
        
        # No values provided
        raise HTTPException(status_code=400, detail=f"{field_name} cannot be empty")

    # Handle logo upload
    logo_url = None
    if logo:
        try:
            logo_url = await save_upload_file(logo)
            if logo_url:
                # Convert to full URL path
                logo_url = f"/{logo_url}"  # This will be served by FastAPI static files
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    # Parse list fields (now properly receives all values)
    description_list = parse_list_field("description", description)
    responsibilities_list = parse_list_field("responsibilities", responsibilities)
    soft_skills_list = parse_list_field("soft_skills", soft_skills)
    qualifications_list = parse_list_field("qualifications", qualifications)
    
    # Validate that lists are not empty
    if not description_list:
        raise HTTPException(status_code=400, detail="description cannot be empty")
    if not responsibilities_list:
        raise HTTPException(status_code=400, detail="responsibilities cannot be empty")
    if not soft_skills_list:
        raise HTTPException(status_code=400, detail="soft_skills cannot be empty")
    if not qualifications_list:
        raise HTTPException(status_code=400, detail="qualifications cannot be empty")
    
    # Create job
    new_job = Job(
        title=title,
        company=company,
        location=location,
        experience=experience,
        salary=salary,
        type=type,
        category=category,
        logo_url=logo_url,
        description=json.dumps(description_list),
        responsibilities=json.dumps(responsibilities_list),
        soft_skills=json.dumps(soft_skills_list),
        qualifications=json.dumps(qualifications_list)
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    return new_job.to_dict()


@router.put("/{job_id}", response_model=dict)
def update_job(job_id: int, job_update: JobUpdate, db: Session = Depends(get_db)):
    """
    Update an existing job posting
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Update only provided fields
    update_data = job_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        # Convert list fields to JSON strings
        if field in ["description", "responsibilities", "soft_skills", "qualifications"]:
            if value is not None:
                setattr(job, field, json.dumps(value))
        elif field == "logo_url":
            setattr(job, field, value)
        else:
            setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    
    return job.to_dict()

@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """
    Delete a job posting
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    
    return None

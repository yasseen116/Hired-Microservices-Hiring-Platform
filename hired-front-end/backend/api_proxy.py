from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Header, Request
from fastapi.responses import JSONResponse, StreamingResponse
import requests
import json
from typing import Optional, List

router = APIRouter(prefix="/api")

# Microservice URLs - use localhost when running with bash script
# For Docker, change these to: http://job-service:8000, etc.
JOB_SERVICE = "http://localhost:8000"
AUTH_SERVICE = "http://localhost:8002"
APP_SERVICE = "http://localhost:8003"

# ========== AUTH ENDPOINTS ==========

@router.post("/auth/login")
async def login(email: str = Form(...), password: str = Form(...)):
    try:
        response = requests.post(f"{AUTH_SERVICE}/api/auth/login",
            json={"email": email, "password": password})
        try:
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except:
            return JSONResponse(content={"detail": response.text or "Auth service error"}, status_code=response.status_code)
    except requests.exceptions.ConnectionError:
        return JSONResponse(content={"detail": "Auth service is not available"}, status_code=503)

@router.post("/auth/signup")
async def signup(
    email: str = Form(...), 
    password: str = Form(...), 
    name: str = Form(...),
    role: str = Form("seeker"),
    company_name: Optional[str] = Form(None)
):
    try:
        response = requests.post(f"{AUTH_SERVICE}/api/auth/signup",
            json={"email": email, "password": password, "name": name, "role": role, "company_name": company_name})
        try:
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except:
            return JSONResponse(content={"detail": response.text or "Auth service error"}, status_code=response.status_code)
    except requests.exceptions.ConnectionError:
        return JSONResponse(content={"detail": "Auth service is not available"}, status_code=503)

@router.get("/auth/me")
async def get_profile(authorization: str = Header(None)):
    try:
        response = requests.get(f"{AUTH_SERVICE}/api/auth/me",
            headers={"Authorization": authorization})
        try:
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except:
            return JSONResponse(content={"detail": response.text or "Auth service error"}, status_code=response.status_code)
    except requests.exceptions.ConnectionError:
        return JSONResponse(content={"detail": "Auth service is not available"}, status_code=503)

@router.put("/auth/profile")
async def update_profile(
    job_title: Optional[str] = Form(None),
    skills: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    about: Optional[str] = Form(None),
    experience: Optional[str] = Form(None),
    education: Optional[str] = Form(None),
    authorization: str = Header(None)
):
    data = {}
    if job_title: data["job_title"] = job_title
    if skills: data["skills"] = json.loads(skills)
    if phone: data["phone"] = phone
    if location: data["location"] = location
    if about: data["about"] = about
    if experience: data["experience"] = json.loads(experience)
    if education: data["education"] = json.loads(education)
    
    try:
        response = requests.put(f"{AUTH_SERVICE}/api/auth/profile",
            json=data, headers={"Authorization": authorization})
        try:
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except:
            return JSONResponse(content={"detail": response.text or "Auth service error"}, status_code=response.status_code)
    except requests.exceptions.ConnectionError:
        return JSONResponse(content={"detail": "Auth service is not available"}, status_code=503)

@router.post("/auth/profile/photo")
async def upload_photo(file: UploadFile = File(...), authorization: str = Header(None)):
    files = {"file": (file.filename, file.file, file.content_type)}
    response = requests.post(f"{AUTH_SERVICE}/api/auth/profile/photo",
        files=files, headers={"Authorization": authorization})
    return JSONResponse(content=response.json(), status_code=response.status_code)

@router.delete("/auth/profile/photo")
async def delete_photo(authorization: str = Header(None)):
    response = requests.delete(f"{AUTH_SERVICE}/api/auth/profile/photo",
        headers={"Authorization": authorization})
    return JSONResponse(content=response.json(), status_code=response.status_code)

@router.post("/auth/profile/cv")
async def upload_cv(file: UploadFile = File(...), authorization: str = Header(None)):
    files = {"file": (file.filename, file.file, file.content_type)}
    response = requests.post(f"{AUTH_SERVICE}/api/auth/profile/cv",
        files=files, headers={"Authorization": authorization})
    return JSONResponse(content=response.json(), status_code=response.status_code)

@router.delete("/auth/profile/cv")
async def delete_cv(authorization: str = Header(None)):
    response = requests.delete(f"{AUTH_SERVICE}/api/auth/profile/cv",
        headers={"Authorization": authorization})
    return JSONResponse(content=response.json(), status_code=response.status_code)

# ========== FILE PROXY ==========

def _stream_file(response: requests.Response):
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="File not found")
    headers = {}
    content_type = response.headers.get("content-type")
    if content_type:
        headers["Content-Type"] = content_type
    content_disposition = response.headers.get("content-disposition")
    if content_disposition:
        headers["Content-Disposition"] = content_disposition
    return StreamingResponse(response.iter_content(chunk_size=1024 * 128),
        status_code=response.status_code, headers=headers)

@router.get("/uploads/{path:path}")
async def proxy_auth_uploads(path: str):
    response = requests.get(f"{AUTH_SERVICE}/uploads/{path}", stream=True)
    return _stream_file(response)

@router.get("/job-uploads/{path:path}")
async def proxy_job_uploads(path: str):
    response = requests.get(f"{JOB_SERVICE}/uploads/{path}", stream=True)
    return _stream_file(response)

@router.get("/app-uploads/{path:path}")
async def proxy_app_uploads(path: str):
    response = requests.get(f"{APP_SERVICE}/uploads/{path}", stream=True)
    return _stream_file(response)

# ========== JOB ENDPOINTS ==========

@router.get("/jobs")
async def get_jobs(
    category: Optional[str] = None,
    type: Optional[str] = None,
    location: Optional[str] = None
):
    params = {}
    if category: params["category"] = category
    if type: params["type"] = type
    if location: params["location"] = location
    response = requests.get(f"{JOB_SERVICE}/api/jobs", params=params)
    return response.json()

@router.get("/jobs/{job_id}")
async def get_job(job_id: int):
    response = requests.get(f"{JOB_SERVICE}/api/jobs/{job_id}")
    return JSONResponse(content=response.json(), status_code=response.status_code)

@router.get("/jobs/{job_id}/similar")
async def get_similar_jobs(job_id: int):
    response = requests.get(f"{JOB_SERVICE}/api/jobs/{job_id}/similar")
    return response.json()

@router.post("/jobs")
async def create_job(
    title: str = Form(...),
    company: str = Form(...),
    location: str = Form(...),
    experience: str = Form(...),
    salary: str = Form(...),
    type: str = Form(...),
    category: str = Form(...),
    description: List[str] = Form(...),
    responsibilities: List[str] = Form(...),
    soft_skills: List[str] = Form(...),
    qualifications: List[str] = Form(...),
    logo: Optional[UploadFile] = File(None),
    logo_url: Optional[str] = Form(None)
):
    # Build form data
    data = {
        "title": title, "company": company, "location": location,
        "experience": experience, "salary": salary, "type": type,
        "category": category
    }
    
    # Add lists as multiple form entries
    form_data = []
    for key, value in data.items():
        form_data.append((key, value))
    for desc in description:
        form_data.append(("description", desc))
    for resp in responsibilities:
        form_data.append(("responsibilities", resp))
    for skill in soft_skills:
        form_data.append(("soft_skills", skill))
    for qual in qualifications:
        form_data.append(("qualifications", qual))
    
    if logo_url:
        form_data.append(("logo_url", logo_url))
    
    files = {}
    if logo:
        files["logo"] = (logo.filename, logo.file, logo.content_type)
    
    response = requests.post(f"{JOB_SERVICE}/api/jobs/with-logo",
        data=form_data, files=files)
    return JSONResponse(content=response.json(), status_code=response.status_code)

@router.put("/jobs/{job_id}")
async def update_job(job_id: int, data: dict):
    response = requests.put(f"{JOB_SERVICE}/api/jobs/{job_id}", json=data)
    return JSONResponse(content=response.json(), status_code=response.status_code)

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: int):
    response = requests.delete(f"{JOB_SERVICE}/api/jobs/{job_id}")
    return JSONResponse(content=response.json(), status_code=response.status_code)

# ========== APPLICATION ENDPOINTS ==========

@router.post("/applications")
async def submit_application(
    job_id: int = Form(...),
    cv: Optional[UploadFile] = File(None),
    authorization: str = Header(None)
):
    data = {"job_id": job_id}
    files = {}
    if cv:
        files["cv"] = (cv.filename, cv.file, cv.content_type)
    
    response = requests.post(f"{APP_SERVICE}/api/applications/",
        data=data, files=files, headers={"Authorization": authorization})
    return JSONResponse(content=response.json(), status_code=response.status_code)

@router.get("/applications/my")
async def get_my_applications(authorization: str = Header(None)):
    response = requests.get(f"{APP_SERVICE}/api/applications/my",
        headers={"Authorization": authorization})
    return response.json()

@router.get("/applications/check/{job_id}")
async def check_applied(job_id: int, authorization: str = Header(None)):
    response = requests.get(f"{APP_SERVICE}/api/applications/check/{job_id}",
        headers={"Authorization": authorization})
    return response.json()

@router.get("/applications/job/{job_id}")
async def get_applications_for_job(job_id: int, authorization: str = Header(None)):
    headers = {"Authorization": authorization} if authorization else {}
    response = requests.get(f"{APP_SERVICE}/api/applications/job/{job_id}", headers=headers)
    return JSONResponse(content=response.json(), status_code=response.status_code)

@router.get("/applications/{app_id}")
async def get_application(app_id: int, authorization: str = Header(None)):
    response = requests.get(f"{APP_SERVICE}/api/applications/{app_id}",
        headers={"Authorization": authorization})
    return JSONResponse(content=response.json(), status_code=response.status_code)

@router.put("/applications/{app_id}/status")
async def update_application_status(app_id: int, request: Request, authorization: str = Header(None)):
    payload = await request.json()
    headers = {"Authorization": authorization} if authorization else {}
    response = requests.put(f"{APP_SERVICE}/api/applications/{app_id}/status",
        json=payload, headers=headers)
    return JSONResponse(content=response.json(), status_code=response.status_code)

@router.delete("/applications/{app_id}")
async def withdraw_application(app_id: int, authorization: str = Header(None)):
    response = requests.delete(f"{APP_SERVICE}/api/applications/{app_id}",
        headers={"Authorization": authorization})
    return JSONResponse(content=response.json(), status_code=response.status_code)

@router.get("/applications/job/{job_id}")
async def get_job_applications(job_id: int):
    response = requests.get(f"{APP_SERVICE}/api/applications/job/{job_id}")
    return response.json()

@router.put("/applications/{app_id}/status")
async def update_app_status(app_id: int, status: str = Form(...)):
    response = requests.put(f"{APP_SERVICE}/api/applications/{app_id}/status",
        json={"status": status})
    return JSONResponse(content=response.json(), status_code=response.status_code)

@router.delete("/applications/{app_id}")
async def withdraw_application(app_id: int, authorization: str = Header(None)):
    response = requests.delete(f"{APP_SERVICE}/api/applications/{app_id}",
        headers={"Authorization": authorization})
    return JSONResponse(content=response.json(), status_code=response.status_code)

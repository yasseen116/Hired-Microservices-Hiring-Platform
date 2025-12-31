# Job Service Backend

FastAPI-based microservice for job management operations with SQLAlchemy ORM and SQLite database.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

### 3. Populate Sample Data (Optional)

```bash
python seed_data.py
```

### 4. Access API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation

## 📁 Project Structure

```
jobs service/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration and session management
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic validation schemas
├── routes.py            # API endpoints
├── requirements.txt     # Python dependencies
├── seed_data.py         # Sample data population script
├── .env.example         # Environment variables template
└── jobs.db             # SQLite database (created automatically)
```

## 🔌 API Endpoints

### Jobs

- **GET** `/api/jobs` - List all jobs (with filtering)
  - Query params: `type`, `city`, `category`, `skip`, `limit`
- **GET** `/api/jobs/{job_id}` - Get job details
- **GET** `/api/jobs/{job_id}/similar` - Get similar jobs
- **POST** `/api/jobs` - Create new job (JSON body)
- **POST** `/api/jobs/with-logo` - Create new job with logo upload (Form data)
- **PUT** `/api/jobs/{job_id}` - Update job
- **DELETE** `/api/jobs/{job_id}` - Delete job

### Static Files

- **GET** `/uploads/{filename}` - Retrieve uploaded logo files

### Health Check

- **GET** `/` - Health check
- **GET** `/health` - Health status

---

## 📤 File Upload Guide

### Creating Jobs with Logo Upload

The API supports two methods for creating jobs:

#### 1. JSON Body (without logo file)
Use `POST /api/jobs` with `Content-Type: application/json`

#### 2. Form Data (with logo file)
Use `POST /api/jobs/with-logo` with `Content-Type: multipart/form-data`

**Supported Image Formats:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`

**Form Fields:**
- `title` (text)
- `company` (text)
- `location` (text)
- `experience` (text)
- `salary` (text)
- `type` (text)
- `category` (text)
- `description` (JSON string) - e.g., `["Point 1", "Point 2"]`
- `responsibilities` (JSON string)
- `soft_skills` (JSON string)
- `qualifications` (JSON string)
- `logo` (file, optional)

**Response:**
- Logo URL will be in format: `/uploads/uuid.extension`
- Full URL: `http://localhost:8000/uploads/uuid.extension`

### Example: Upload with cURL

```bash
curl -X POST http://localhost:8000/api/jobs/with-logo \
  -F 'title=Backend Developer' \
  -F 'company=Tech Inc' \
  -F 'location=Cairo' \
  -F 'experience=2-3 years' \
  -F 'salary=20,000 EGP' \
  -F 'type=Hybrid' \
  -F 'category=Software' \
  -F 'description=["Build APIs", "Write clean code"]' \
  -F 'responsibilities=["Develop features", "Code review"]' \
  -F 'soft_skills=["Communication", "Teamwork"]' \
  -F 'qualifications=["CS Degree", "Python experience"]' \
  -F 'logo=@/path/to/company-logo.png'
```

### Example: Upload with Python

```python
import requests

url = "http://localhost:8000/api/jobs/with-logo"

# Prepare form data
data = {
    'title': 'Backend Developer',
    'company': 'Tech Inc',
    'location': 'Cairo',
    'experience': '2-3 years',
    'salary': '20,000 EGP',
    'type': 'Hybrid',
    'category': 'Software',
    'description': '["Build APIs", "Write clean code"]',
    'responsibilities': '["Develop features", "Code review"]',
    'soft_skills': '["Communication", "Teamwork"]',
    'qualifications': '["CS Degree", "Python experience"]'
}

# Prepare file
files = {
    'logo': ('company-logo.png', open('company-logo.png', 'rb'), 'image/png')
}

response = requests.post(url, data=data, files=files)
print(response.json())
```

### Example: Upload with JavaScript/Fetch

```javascript
const formData = new FormData();
formData.append('title', 'Backend Developer');
formData.append('company', 'Tech Inc');
formData.append('location', 'Cairo');
formData.append('experience', '2-3 years');
formData.append('salary', '20,000 EGP');
formData.append('type', 'Hybrid');
formData.append('category', 'Software');
formData.append('description', JSON.stringify(['Build APIs', 'Write clean code']));
formData.append('responsibilities', JSON.stringify(['Develop features', 'Code review']));
formData.append('soft_skills', JSON.stringify(['Communication', 'Teamwork']));
formData.append('qualifications', JSON.stringify(['CS Degree', 'Python experience']));

// Add logo file
const fileInput = document.querySelector('input[type="file"]');
formData.append('logo', fileInput.files[0]);

fetch('http://localhost:8000/api/jobs/with-logo', {
  method: 'POST',
  body: formData
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 🔍 Example Usage

### Get all jobs
```bash
curl http://localhost:8000/api/jobs
```

### Filter jobs by category
```bash
curl "http://localhost:8000/api/jobs?category=Software&type=Remote"
```

### Create a new job
```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Backend Developer",
    "company": "Tech Inc",
    "location": "Cairo",
    "experience": "2-3 years",
    "salary": "20,000 - 30,000 EGP",
    "type": "Hybrid",
    "category": "Software",
    "logo_url": null,
    "description": ["Build APIs", "Write clean code"],
    "responsibilities": ["Develop features", "Code review"],
    "soft_skills": ["Communication", "Teamwork"],
    "qualifications": ["CS Degree", "Python experience"]
  }'
```

## 🎨 Frontend Integration

The backend is configured with CORS to allow frontend access. Update your frontend JavaScript to point to:
- Development: `http://localhost:8000/api/jobs`
- Production: Update CORS settings in `main.py`

## 🗃️ Database Schema

### Job Table

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key (auto-increment) |
| title | String | Job title |
| company | String | Company name |
| location | String | Job location/city |
| experience | String | Required experience |
| salary | String | Salary range |
| type | String | On-site/Hybrid/Remote |
| category | String | Job category |
| logo_url | String | Company logo URL (optional) |
| description | JSON | Job description (array) |
| responsibilities | JSON | Job responsibilities (array) |
| soft_skills | JSON | Required soft skills (array) |
| qualifications | JSON | Required qualifications (array) |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

## 📝 Notes

- SQLite database (`jobs.db`) is created automatically on first run
- All timestamps are in UTC
- JSON fields are stored as TEXT and parsed automatically
- CORS is configured for development (allow all origins)
- In production, update CORS settings to restrict allowed origins

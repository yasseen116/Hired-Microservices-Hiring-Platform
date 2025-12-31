# Hired – Job Search & Recruitment Platform

Complete job marketplace platform with job seeker and employer features.

## 🚀 Project Overview
**Hired** is a full-stack job marketplace with a FastAPI frontend (proxy layer), microservices backend, and role-based features. Job seekers can browse jobs, apply, save to wishlist, and manage applications. Employers can post jobs, manage listings, and review candidates. The system includes user authentication, profiles, and comprehensive dashboards for both user types.

---

## 🧰 Technology
- **Frontend Layer:** FastAPI + Jinja2 templates (server-rendered pages at `localhost:5000`)
- **Frontend UI:** HTML, CSS, JavaScript, Vue.js
- **API Proxy:** Frontend proxies requests to microservices (`/api/uploads`, `/api/jobs`, `/api/auth`, `/api/applications`)
- **Microservices:**
  - Auth Service (`localhost:8002`) – user registration, login, profiles, photo/CV uploads
  - Job Service (`localhost:8000`) – job listings, management
  - Application Service (`localhost:8003`) – job applications, candidate tracking
- **Database:** SQLite per service (SQLAlchemy ORM)
- **Static assets:** `/static` (CSS, JS, images)
- **Dev server:** Uvicorn with hot-reload

> Files of interest:
> - Frontend proxy: `hired-front-end/backend/api_proxy.py`
> - Frontend models: `hired-front-end/static/js/model.js` (Vue.js client logic)
> - Auth models: `auth-service/auth-service/models.py`
> - Job models: `job-service/jobs-service/models.py` 

---

## ✨ Features

### Job Seekers
- Browse and search job listings
- View detailed job information with similar job suggestions
- Apply to jobs with optional message
- Save/unsave jobs to wishlist
- User profile with skills, experience, education
- Application history and status tracking
- Profile photo and CV uploads

### Employers/Job Providers
- Post and manage job listings
- Dashboard overview of posted jobs
- Review and manage applications
- Accept/reject candidates
- Track hiring metrics
- Company profile setup

---

## 🖼️ Gallery
See the full walkthrough with screenshots: [`gallery.md`](gallery.md)

---

## 🧭 Project Structure
```
Hired/
├── hired-front-end/           # Frontend proxy layer (FastAPI + templates)
│   ├── app.py                 # Main FastAPI app
│   ├── backend/
│   │   ├── api_proxy.py       # Microservice proxy routes
│   │   ├── database.py        # Local SQLite setup
│   │   └── models/            # SQLAlchemy models (frontend-only)
│   ├── static/                # CSS, JavaScript, images
│   ├── templates/             # Jinja2 templates
│   └── requirements.txt
├── auth-service/              # Authentication microservice
│   └── auth-service/
│       ├── main.py
│       ├── routes.py
│       ├── models.py
│       └── file_utils.py      # Photo/CV upload handling
├── job-service/               # Job listings microservice
│   └── jobs-service/
│       ├── main.py
│       ├── routes.py
│       └── models.py
├── omar-application-service/  # Applications microservice
│   ├── main.py
│   ├── routes.py
│   └── models.py
├── start-services.ps1         # PowerShell startup script
├── start-services.sh          # Bash startup script
└── docker-compose.yml         # Docker Compose configuration
```

---

## 🏛 Architecture Patterns
- **Frontend (MVC):** The frontend follows an **MVC** pattern — `templates/` act as *Views*, `static/js/` contains *Controllers* (e.g., `main.js`, `browse-jobs.js`), and `static/js/model.js` acts as the client-side *Model* that communicates with backend APIs. This helps keep UI, state, and data access concerns separated.
- **Backend (Microservices):** The backend is intended to use a **microservices** architecture — split functionality into small, focused services (for example: `auth-service`, `jobs-service`, `applications-service`). Each service owns its data and exposes a clear HTTP API under `/api` so services can be developed and deployed independently.

---


## 🔌 API Endpoints

### Frontend Proxy Routes (`/api`)
- `POST /api/auth/login` – User login
- `POST /api/auth/signup` – User registration
- `GET /api/auth/me` – Current user profile
- `PUT /api/auth/profile` – Update profile
- `POST /api/auth/profile/photo` – Upload profile photo
- `GET /api/jobs` – List jobs with filters
- `GET /api/jobs/{id}` – Job details
- `GET /api/jobs/{id}/similar` – Similar jobs
- `POST /api/applications` – Submit job application
- `GET /api/applications` – User's applications
- `GET /api/uploads/{path}` – Access uploaded files (photos, CVs)

### Direct Microservice Endpoints
- **Auth Service** (`localhost:8002/api/auth/*`)
- **Job Service** (`localhost:8000/api/jobs/*`)
- **Application Service** (`localhost:8003/api/applications/*`)

---

## Diagrams ✅

### Context Diagram
![Context Diagram](hired-front-end/static/images/Diagrams/Context%20diagram.jpg)

### Class Diagram
![Class Diagram](hired-front-end/static/images/Diagrams/class%20diagram.jpg)

### Use Case Diagram
![Use Case Diagram](hired-front-end/static/images/Diagrams/use%20case%20diagram.jpg)

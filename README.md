# Hired (Job seeking Project) — Documentation

A short, focused reference for the Hired frontend (a.k.a. fitnessWay).

## 🚀 Project Overview
**Hired** is a job listing and application front-end with server-backed data. It includes pages for browsing jobs, viewing job details, user registration and login, a wishlist (saved jobs), and a dashboard for users.

---

## 🧰 Technology
- **Frontend:** HTML, CSS, JavaScript , vue.js 
- **Templating:** Jinja2 templates in `/templates` (server-rendered pages)
- **Backend (API):** FastAPI (expected API base: `http://127.0.0.1:8000/api`)
- **Database:** SQLite (SQLAlchemy models in `backend/models/`)
- **ORM:** SQLAlchemy
- **Static assets:** `/static` (CSS, JS, images)
- **Dev server:** uvicorn (see `requirements.txt`)
- **Architecture:** Frontend follows an **MVC** pattern (templates = Views, `static/js` = Controllers, `static/js/model.js` = client Models). Backend is designed for a **microservices** architecture (e.g., `auth-service`, `jobs-service`, `applications-service`).

> Files of interest:
> - SQLAlchemy models: `backend/models/*.py` (User, Job, Application, Skill, SavedJob)
> - Client API usage: `static/js/model.js` (uses `http://127.0.0.1:8000/api`) 

---

## ✨ Features
- Browse and search job listings
- Job details page with similar-job suggestions
- Apply to jobs (front-end application submission simulation)
- Save/unsave jobs to a **Wishlist**
- User profile and dashboard pages
- Mock/company sections showing top companies
- Server-side models: Users, Jobs, Applications, Skills, Saved Jobs

---

## 🖼️ Gallery
See the full walkthrough with screenshots: [`gallery.md`](gallery.md)

---

## 🧭 Project Structure (high level)
- `app.py` — (placeholder) app entry (if present)
- `backend/` — database configuration and models
- `preview/` — static HTML previews you can open locally
- `templates/` — server-rendered templates
- `static/` — `css/`, `js/`, `images/`

---

## 🏛 Architecture Patterns
- **Frontend (MVC):** The frontend follows an **MVC** pattern — `templates/` act as *Views*, `static/js/` contains *Controllers* (e.g., `main.js`, `browse-jobs.js`), and `static/js/model.js` acts as the client-side *Model* that communicates with backend APIs. This helps keep UI, state, and data access concerns separated.
- **Backend (Microservices):** The backend is intended to use a **microservices** architecture — split functionality into small, focused services (for example: `auth-service`, `jobs-service`, `applications-service`). Each service owns its data and exposes a clear HTTP API under `/api` so services can be developed and deployed independently.

---


## 🔌 API (expected / common endpoints)
The front-end JS calls these endpoints via `static/js/model.js`:
- GET `/api/jobs` — list jobs
- GET `/api/jobs/{id}` — job details
- GET `/api/jobs/{id}/similar` — similar jobs

Note: The repo expects a FastAPI backend; implement endpoints under `/api` to match the client calls.

---

## Diagrams ✅

### Context Diagram
![Context Diagram](static/images/Diagrams/Context%20diagram.jpg)

### Class Diagram
![Class Diagram](static/images/Diagrams/class%20diagram.jpg)

### Use Case Diagram
![Use Case Diagram](static/images/Diagrams/use%20case%20diagram.jpg)

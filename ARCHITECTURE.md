# Hired Platform Architecture Walkthrough (5-Person Split)

This walkthrough explains how the Hired platform is structured and how the services interact. It is divided across five people: two focused on the frontend and three on the backend.

## Person 1 (Frontend): UI Shell and Page Structure

- The frontend lives in `hired-front-end/` and serves HTML via FastAPI + Jinja templates.
- Each page is a Jinja template in `hired-front-end/templates/` (e.g., `index.html`, `browse-jobs.html`, `job-details.html`, `profile.html`, `dashboard.html`).
- Global navigation and layout are defined in `hired-front-end/templates/_base.html`.
- Static assets (CSS/JS/images) live in `hired-front-end/static/`.
- Routes are defined in `hired-front-end/app.py` and map friendly URLs like `/browse-jobs` to template pages (no `.html` in routes).

## Person 2 (Frontend): Page Logic, API Model, and UX Flows

- Each page’s interactive logic is a Vue app in `hired-front-end/static/js/` (e.g., `browse-jobs.js`, `job-details.js`, `profile.js`, `dashboard.js`).
- `hired-front-end/static/js/model.js` centralizes API calls (auth, jobs, applications) and normalizes upload URLs.
- The frontend talks to a same‑origin API proxy at `/api/*` (defined in `hired-front-end/backend/api_proxy.py`) to avoid CORS issues.
- User sessions are stored in `localStorage` (JWT token + user payload), and all authenticated calls use `Authorization: Bearer <token>`.
- UX flows:
  - Seekers browse jobs, apply with stored or new CV, and track applications in the profile page.
  - Providers manage jobs and review applications in the dashboard.

## Person 3 (Backend): Auth Service

- Location: `auth-service/auth-service/`
- Core responsibilities:
  - User signup/login with JWT issuance.
  - Profile management (skills, experience, education, contact info).
  - File uploads for profile photos and CVs, served under `/uploads/`.
- The auth service stores data in `auth.db` (SQLite) by default.
- JWT verification endpoint `/api/auth/verify` is used by other services.
- Providers can request limited applicant info via `/api/auth/users/{user_id}`.

## Person 4 (Backend): Job Service

- Location: `job-service/jobs-service/`
- Core responsibilities:
  - Job CRUD operations.
  - Logo upload via `/api/jobs/with-logo` (multipart form data).
  - Job search and “similar jobs” endpoint.
- Logos are stored under `/uploads/` and the service returns `logoUrl`.
- Data is stored in `jobs.db` (SQLite) by default.

## Person 5 (Backend): Application Service

- Location: `omar-application-service/`
- Core responsibilities:
  - Submit applications with optional CV upload.
  - Prevent duplicate applications.
  - Track status changes (pending/accepted/rejected).
- The service verifies JWTs via the auth service `/api/auth/verify`.
- It enriches applications with job data (job title/company) and, for providers, applicant info pulled from the auth service.
- Data is stored in `applications.db` (SQLite) by default.

## How Services Connect

- Frontend calls `/api/*` on the frontend server.
- The frontend API proxy forwards to:
  - Auth service: `http://localhost:8002`
  - Job service: `http://localhost:8000`
  - Application service: `http://localhost:8003`
- Uploads are proxied through:
  - `/api/uploads/*` (auth uploads)
  - `/api/job-uploads/*` (job logos)
  - `/api/app-uploads/*` (application CVs)

## Ports in Dev Mode

- Frontend: `http://localhost:5000`
- Job service: `http://localhost:8000`
- Auth service: `http://localhost:8002`
- Application service: `http://localhost:8003`

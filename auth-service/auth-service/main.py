# ==============================================================================
# MAIN APPLICATION MODULE
# ==============================================================================
# This is the entry point for the Authentication Service.
# It sets up the FastAPI application with all necessary configurations:
# 1. CORS (Cross-Origin Resource Sharing) for frontend integration
# 2. Static file serving for uploaded photos and CVs
# 3. Route registration
# 4. Database table creation
#
# The service will be available at http://localhost:8001
# API documentation at http://localhost:8001/docs
# ==============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from routes import router
import os

# ==============================================================================
# CREATE DATABASE TABLES
# ==============================================================================
# This line creates all tables defined in our models (User table).
# It uses the SQLAlchemy "metadata" which contains info about all tables.
# 
# The tables are only created if they don't already exist.
# Existing tables and data are preserved.
# ==============================================================================
Base.metadata.create_all(bind=engine)

# ==============================================================================
# INITIALIZE FASTAPI APP
# ==============================================================================
# FastAPI is the web framework we use to create the API.
# The parameters here configure the automatic documentation.
# ==============================================================================
app = FastAPI(
    title="Authentication Service API",
    description="""
    Microservice for user authentication and profile management.
    
    ## Features
    - User registration with email and password
    - JWT-based authentication
    - Profile management (skills, experience, education)
    - File uploads (profile photo, CV)
    
    ## Authentication
    After login or signup, you receive a JWT token.
    Include it in subsequent requests as:
    `Authorization: Bearer <your_token>`
    """,
    version="1.0.0",
    docs_url="/docs",      # Swagger UI URL
    redoc_url="/redoc"     # ReDoc URL (alternative docs)
)

# ==============================================================================
# CORS CONFIGURATION
# ==============================================================================
# CORS (Cross-Origin Resource Sharing) controls which websites can call our API.
# 
# By default, browsers block requests from one domain to another (security).
# CORS headers tell browsers "it's OK for these websites to call me."
#
# In development, we allow all origins ("*") for convenience.
# In production, you should restrict this to your frontend domain only:
# allow_origins=["https://yourfrontend.com"]
# ==============================================================================
app.add_middleware(
    CORSMiddleware,
    # Which origins (domains) can call this API
    # In production, replace "*" with your actual frontend URL
    allow_origins=["*"],
    
    # Allow cookies and authentication headers
    allow_credentials=True,
    
    # Which HTTP methods are allowed
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    
    # Which headers can be included in requests
    allow_headers=["*"],  # Accept any headers (including Authorization)
)

# ==============================================================================
# STATIC FILE SERVING
# ==============================================================================
# Mount the uploads directory to serve uploaded files (photos, CVs).
# 
# After mounting:
# - A file at uploads/photos/abc.jpg
# - Can be accessed at http://localhost:8001/uploads/photos/abc.jpg
#
# We create the directories if they don't exist.
# ==============================================================================

# Create uploads directories if they don't exist
uploads_dir = "uploads"
photos_dir = os.path.join(uploads_dir, "photos")
cvs_dir = os.path.join(uploads_dir, "cvs")

for directory in [uploads_dir, photos_dir, cvs_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Mount the uploads directory as a static file server
# name="uploads" is used for URL generation with url_for()
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# ==============================================================================
# REGISTER ROUTES
# ==============================================================================
# Include all the routes from our router module.
# The router has prefix="/api/auth", so routes become:
# - /api/auth/signup
# - /api/auth/login
# - etc.
# ==============================================================================
app.include_router(router)

# ==============================================================================
# HEALTH CHECK ENDPOINTS
# ==============================================================================
# These endpoints are used to check if the service is running.
# Useful for:
# - Load balancers to check service health
# - Kubernetes liveness/readiness probes
# - Monitoring systems
# ==============================================================================

@app.get("/", tags=["health"])
def root():
    """
    Root endpoint - confirms the service is running.
    
    Returns a simple message with service info.
    """
    return {
        "status": "healthy",
        "service": "Authentication Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint for monitoring systems.
    
    Returns simple OK status.
    """
    return {"status": "ok"}




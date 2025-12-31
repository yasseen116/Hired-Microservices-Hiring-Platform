from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine
import models
from routes import router
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=os.getenv("APP_NAME", "Application Service"),
    description="Microservice for managing job applications",
    version=os.getenv("APP_VERSION", "1.0.0")
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory and mount static files
uploads_dir = "uploads"
os.makedirs(os.path.join(uploads_dir, "cvs"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Routes
app.include_router(router, prefix="/api/applications", tags=["Applications"])

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "healthy",
        "service": os.getenv("APP_NAME", "Application Service"),
        "version": os.getenv("APP_VERSION", "1.0.0")
    }

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
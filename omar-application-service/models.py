from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base
from datetime import datetime

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    job_id = Column(Integer, nullable=False, index=True)
    status = Column(String(50), default="pending", index=True)  # pending, accepted, rejected
    
    # CV upload support
    cv_name = Column(String(255), nullable=True)
    cv_url = Column(String(500), nullable=True)
    
    # Optional cover letter
    cover_letter = Column(Text, nullable=True)
    
    # Timestamps
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "jobId": self.job_id,
            "status": self.status,
            "cvName": self.cv_name,
            "cvUrl": self.cv_url,
            "coverLetter": self.cover_letter,
            "appliedAt": self.applied_at.isoformat() if self.applied_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
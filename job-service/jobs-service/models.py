from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base
import json

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    experience = Column(String(100), nullable=False)
    salary = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False, index=True)  # On-site, Hybrid, Remote
    category = Column(String(100), nullable=False, index=True)  # Accounting, Sales, Software, etc.
    logo_url = Column(String(500), nullable=True)
    
    # JSON fields stored as TEXT
    description = Column(Text, nullable=False)  # JSON array as string
    responsibilities = Column(Text, nullable=False)  # JSON array as string
    soft_skills = Column(Text, nullable=False)  # JSON array as string
    qualifications = Column(Text, nullable=False)  # JSON array as string
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert model to dictionary with JSON parsing for array fields"""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "experience": self.experience,
            "salary": self.salary,
            "type": self.type,
            "category": self.category,
            "logoUrl": self.logo_url,
            "description": json.loads(self.description) if self.description else [],
            "responsibilities": json.loads(self.responsibilities) if self.responsibilities else [],
            "softSkills": json.loads(self.soft_skills) if self.soft_skills else [],
            "qualifications": json.loads(self.qualifications) if self.qualifications else [],
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }

from sqlalchemy import Column, Integer, String, Boolean, Text , DateTime
from sqlalchemy.orm import relationship
from backend.database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    #user identity attributes
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    
    # account attributes 
    role = Column(String, nullable=False)  
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # profile fields
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    about_me = Column(Text, nullable=True)
    cv_url = Column(String, nullable=True)

    # relations
    jobs = relationship("Job", back_populates="owner", cascade="all, delete")
    applications = relationship("Application", back_populates="user", cascade="all, delete")
    skills = relationship("Skill", back_populates="user", cascade="all, delete")
    saved_jobs = relationship("SavedJob", back_populates="user", cascade="all, delete")
    
    
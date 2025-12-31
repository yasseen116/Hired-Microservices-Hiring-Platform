# ==============================================================================
# DATABASE CONFIGURATION MODULE
# ==============================================================================
# This module sets up the SQLite database connection using SQLAlchemy ORM.
# It follows the same pattern as the Jobs service for consistency across
# microservices in the Hired platform.
#
# SQLAlchemy is a powerful Python ORM (Object-Relational Mapping) that allows
# us to interact with the database using Python objects instead of raw SQL.
# ==============================================================================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ==============================================================================
# DATABASE URL CONFIGURATION
# ==============================================================================
# SQLite is a file-based database, perfect for development and small projects.
# The URL format is: sqlite:///./filename.db
# - sqlite:/// = SQLite database driver
# - ./ = Current directory
# - auth.db = Database filename
#
# For production, you would typically use PostgreSQL or MySQL:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
# ==============================================================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./auth.db"

# ==============================================================================
# CREATE SQLALCHEMY ENGINE
# ==============================================================================
# The engine is the starting point for any SQLAlchemy application.
# It maintains a pool of database connections that can be reused.
#
# connect_args={"check_same_thread": False}:
# - SQLite by default only allows one thread to communicate with it
# - This setting is needed because FastAPI can handle multiple threads
# - This is only necessary for SQLite, not for other databases
# ==============================================================================
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI
)

# ==============================================================================
# SESSION FACTORY
# ==============================================================================
# SessionLocal is a factory function that creates new database sessions.
# Each session represents a "workspace" for database operations.
#
# autocommit=False: Changes are not automatically saved; you must call commit()
# autoflush=False: Changes are not automatically sent to DB before queries
# bind=engine: Connects this session factory to our database engine
# ==============================================================================
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ==============================================================================
# BASE CLASS FOR MODELS
# ==============================================================================
# All our database models (User, etc.) will inherit from this Base class.
# It provides the declarative system that maps Python classes to database tables.
# ==============================================================================
Base = declarative_base()

# ==============================================================================
# DATABASE SESSION DEPENDENCY
# ==============================================================================
# This function is used as a FastAPI dependency to provide database sessions
# to our route handlers. It implements the "dependency injection" pattern.
#
# How it works:
# 1. When a request comes in, FastAPI calls get_db()
# 2. get_db() creates a new database session
# 3. The session is "yielded" to the route handler
# 4. After the request is complete (or if an error occurs), the finally block
#    ensures the session is properly closed
#
# Usage in routes:
# @router.get("/users")
# def get_users(db: Session = Depends(get_db)):
#     ...
# ==============================================================================
def get_db():
    """
    Creates a database session for each request and ensures it's closed after use.
    
    This is a generator function (uses yield) that:
    1. Creates a new session
    2. Provides it to the route handler
    3. Cleans up by closing the session when done
    
    Returns:
        Session: A SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

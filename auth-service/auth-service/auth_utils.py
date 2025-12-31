# ==============================================================================
# AUTHENTICATION UTILITIES MODULE
# ==============================================================================
# This module provides the core authentication functionality:
# 1. Password hashing and verification using bcrypt
# 2. JWT (JSON Web Token) creation and verification
# 3. FastAPI dependency for protected routes
#
# SECURITY CONCEPTS EXPLAINED:
# 
# PASSWORD HASHING:
# - We NEVER store plain text passwords
# - Instead, we use bcrypt to create a one-way hash
# - When a user logs in, we hash their input and compare hashes
# - Even if the database is compromised, attackers can't get passwords
#
# JWT TOKENS:
# - A JWT is a signed token that contains user information
# - After login, the server creates a token and sends it to the client
# - The client includes this token in all subsequent requests
# - The server verifies the token's signature to authenticate requests
# - Tokens have an expiration time for security
# ==============================================================================

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User

# ==============================================================================
# SECURITY CONFIGURATION
# ==============================================================================
# These settings control how passwords are hashed and how tokens are created.
#
# SECRET_KEY:
# - Used to sign JWT tokens
# - Should be a long, random string in production
# - NEVER commit real secret keys to version control!
# - In production, load this from environment variables
#
# ALGORITHM:
# - HS256 = HMAC with SHA-256
# - This is a symmetric algorithm (same key for signing and verifying)
#
# ACCESS_TOKEN_EXPIRE_DAYS:
# - How long a token is valid
# - After this time, the user must log in again
# ==============================================================================

# In production, load this from environment variables!
# Example: SECRET_KEY = os.getenv("JWT_SECRET_KEY")
SECRET_KEY = "your-secret-key-change-this-in-production-make-it-long-and-random"

# The algorithm used to sign the JWT
ALGORITHM = "HS256"

# Token expiration time (7 days for "remember me" functionality)
ACCESS_TOKEN_EXPIRE_DAYS = 7

# ==============================================================================
# PASSWORD HASHING CONTEXT
# ==============================================================================
# CryptContext from passlib handles password hashing.
#
# schemes=["bcrypt"]:
# - bcrypt is the recommended algorithm for password hashing
# - It's slow by design, making brute-force attacks difficult
# - It automatically handles salting (adding random data to prevent rainbow tables)
#
# deprecated="auto":
# - If we add new schemes in the future, old hashes are marked as deprecated
# - They still work, but new passwords use the latest scheme
# ==============================================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==============================================================================
# HTTP BEARER SECURITY SCHEME
# ==============================================================================
# This tells FastAPI to look for an "Authorization: Bearer <token>" header.
# It's used by the OpenAPI docs to show the authentication requirement.
# 
# auto_error=False:
# - If no token is provided, don't automatically raise an error
# - We handle the error ourselves for better error messages
# ==============================================================================
security = HTTPBearer(auto_error=False)


# ==============================================================================
# PASSWORD UTILITY FUNCTIONS
# ==============================================================================

def hash_password(password: str) -> str:
    """
    Creates a secure hash of a password using bcrypt.
    
    This function is called when:
    1. A new user signs up (to hash their initial password)
    2. A user changes their password
    
    Args:
        password: The plain text password from the user
        
    Returns:
        str: The hashed password (includes salt automatically)
        
    Example:
        >>> hash_password("mypassword123")
        "$2b$12$LQv3c1yZ..."  # Returns a bcrypt hash string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password against its hash.
    
    This function is called during login to check if the provided
    password matches the stored hash.
    
    How it works:
    1. Takes the plain password and hashes it with the same salt
    2. Compares the result with the stored hash
    3. Returns True if they match, False otherwise
    
    Args:
        plain_password: The password provided by the user at login
        hashed_password: The hash stored in the database
        
    Returns:
        bool: True if password matches, False otherwise
        
    Example:
        >>> stored_hash = "$2b$12$LQv3c1yZ..."
        >>> verify_password("mypassword123", stored_hash)
        True
    """
    return pwd_context.verify(plain_password, hashed_password)


# ==============================================================================
# JWT TOKEN FUNCTIONS
# ==============================================================================

def create_access_token(user_id: int, email: str) -> str:
    """
    Creates a JWT access token for a user.
    
    This function is called after successful login or signup to generate
    a token that the client will use for subsequent requests.
    
    JWT Structure:
    - Header: Contains algorithm info (added automatically by jose)
    - Payload: Contains our data (user_id, email, exp)
    - Signature: Cryptographic signature to verify authenticity
    
    Args:
        user_id: The user's database ID
        email: The user's email address
        
    Returns:
        str: The encoded JWT token string
        
    Example:
        >>> create_access_token(123, "john@example.com")
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIi..."
    """
    # Calculate when the token should expire
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    # Create the token payload (the data stored in the token)
    # "sub" is the standard JWT claim for the subject (the user)
    # "exp" is the standard claim for expiration time
    to_encode = {
        "sub": str(user_id),  # Subject: user ID as string (JWT standard)
        "email": email,       # Custom claim: user's email
        "exp": expire         # Expiration time
    }
    
    # Encode the payload and sign it with our secret key
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decodes and verifies a JWT token.
    
    This function:
    1. Verifies the token's signature using our secret key
    2. Checks if the token has expired
    3. Returns the payload if valid, None if invalid
    
    Args:
        token: The JWT token string from the Authorization header
        
    Returns:
        dict: The decoded payload if valid, None if invalid
        
    Example:
        >>> decode_token("eyJhbGci...")
        {"sub": "123", "email": "john@example.com", "exp": 1703123456}
    """
    try:
        # Decode and verify the token
        # This raises JWTError if:
        # - Signature is invalid
        # - Token has expired
        # - Token is malformed
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # Token is invalid or expired
        return None


# ==============================================================================
# FASTAPI DEPENDENCY FOR PROTECTED ROUTES
# ==============================================================================
# This function is used as a FastAPI "dependency" to protect routes.
# It's called automatically before the route handler runs.
#
# Usage in routes:
# @router.get("/protected")
# def protected_route(current_user: User = Depends(get_current_user)):
#     # Only runs if user is authenticated
#     return {"message": f"Hello {current_user.name}"}
# ==============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency that extracts and validates the current user from a JWT token.
    
    This function:
    1. Extracts the token from the Authorization header
    2. Decodes and verifies the token
    3. Looks up the user in the database
    4. Returns the user object or raises an HTTP 401 error
    
    Args:
        credentials: The Authorization header (injected by FastAPI)
        db: Database session (injected by FastAPI)
        
    Returns:
        User: The authenticated user's database record
        
    Raises:
        HTTPException: 401 Unauthorized if token is missing or invalid
        
    Example usage in route:
        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user.to_dict()
    """
    # Define the exception we'll raise if authentication fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Please provide a valid token.",
        headers={"WWW-Authenticate": "Bearer"},  # OAuth2 standard header
    )
    
    # Check if credentials were provided
    if credentials is None:
        raise credentials_exception
    
    # Get the token from the credentials
    token = credentials.credentials
    
    # Decode the token
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID from the token payload
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception
    
    # Look up the user in the database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Account may have been deleted.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# ==============================================================================
# OPTIONAL USER DEPENDENCY
# ==============================================================================
# Similar to get_current_user, but returns None instead of raising an error
# if no token is provided. Useful for routes that work differently for
# authenticated vs unauthenticated users.
# ==============================================================================

async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Like get_current_user, but returns None instead of raising an error.
    
    Useful for routes that have different behavior for authenticated
    vs unauthenticated users.
    
    Args:
        credentials: The Authorization header (may be None)
        db: Database session
        
    Returns:
        User or None: The user if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

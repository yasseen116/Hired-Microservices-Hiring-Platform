# Auth utilities - verifies tokens with the auth service
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

AUTH_SERVICE_URL = "http://localhost:8002"
security = HTTPBearer(auto_error=False)

def verify_token(token: str) -> dict:
    """Call auth service to verify token."""
    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/api/auth/verify",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return None

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """Get current user ID from JWT token."""
    if not credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")
    
    result = verify_token(credentials.credentials)
    if not result or not result.get("valid"):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    
    return result.get("user_id")

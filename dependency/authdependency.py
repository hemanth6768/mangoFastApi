from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from Database.database import get_db
from Repository.authrepository import AuthRepository
from Service.authservice import AuthService
from core.security import verify_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_repository(db: Session = Depends(get_db)):
    return AuthRepository(db)


def get_auth_service(repo: AuthRepository = Depends(get_auth_repository)):
    return AuthService(repo)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    # Postman / Swagger  → sends Authorization: Bearer <token>
    # Browser / Frontend → sends access_token cookie
    token = (
        credentials.credentials
        if credentials
        else request.cookies.get("access_token")
    )

    if not token:
        raise HTTPException(401, "Not authenticated")

    try:
        return verify_access_token(token)
    except Exception:
        raise HTTPException(401, "Invalid or expired access token")


def require_role(role: str):
    def checker(user=Depends(get_current_user)):
        if role not in user.get("roles", []):
            raise HTTPException(403, "Forbidden")
        return user
    return checker


def require_any_role(*roles: str):
    """
    Dependency that checks the user has AT LEAST ONE of the given roles.
    Useful when multiple roles can access the same endpoint.

    Example:
        @router.get("/dashboard")
        def dashboard(user=Depends(require_any_role("Admin", "Seller"))):
            ...
    """
    def checker(user=Depends(get_current_user)):
        user_roles = user.get("roles", [])
        if not any(role in user_roles for role in roles):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: one of {list(roles)} roles required"
            )
        return user
    return checker
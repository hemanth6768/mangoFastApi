import jwt
import secrets
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv


load_dotenv()


ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
 
if not ACCESS_SECRET_KEY:
    raise Exception("ACCESS_SECRET_KEY not set in environment")
if not REFRESH_SECRET_KEY:
    raise Exception("REFRESH_SECRET_KEY not set in environment")
 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
 
 
def create_access_token(data: dict) -> str:
    """
    Creates a short-lived access token.
    Includes 'type': 'access' so it cannot be used as a refresh token.
    """
    payload = data.copy()
    payload["type"] = "access"
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, ACCESS_SECRET_KEY, algorithm=ALGORITHM)
 
 
def create_refresh_token(data: dict) -> str:
    """
    Creates a long-lived refresh token.
    Includes 'type': 'refresh' and a unique 'jti' (JWT ID) for revocation tracking.
    'jti' is stored in the DB via TokenBlocklist to support logout/revocation.
    """
    payload = data.copy()
    payload["type"] = "refresh"
    payload["jti"] = secrets.token_urlsafe(32)
    payload["exp"] = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
 
 
def verify_access_token(token: str) -> dict:
    """
    Decodes and validates an access token.
    Raises jwt.PyJWTError on any failure (expired, wrong type, bad signature).
    """
    payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Token type mismatch: expected access token")
    return payload
 
 
def verify_refresh_token(token: str) -> dict:
    """
    Decodes and validates a refresh token.
    Raises jwt.PyJWTError on any failure.
    Caller must additionally check the jti against the DB blocklist.
    """
    payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("type") != "refresh":
        raise jwt.InvalidTokenError("Token type mismatch: expected refresh token")
    return payload
 
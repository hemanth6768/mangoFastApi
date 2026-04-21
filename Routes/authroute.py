import secrets
import os
from dotenv import load_dotenv
import httpx
from fastapi import APIRouter, Depends, Request, HTTPException, Response
from fastapi.responses import RedirectResponse, JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from Service.authservice import AuthService
from dependency.authdependency import get_auth_service, require_role ,get_current_user
from core.logger import logger

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

load_dotenv()

def get_env(name: str, default: str = None, required: bool = True):
    value = os.getenv(name, default)
    if required and not value:
        raise Exception(f"{name} not set in environment")
    return value


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL")
IS_PROD = os.getenv("ENV", "development") == "production"

# ---------------------------------------------------------------------------
# Limiter — defined at module level so main.py can import it:
#   from app.Route.auth_router import router, limiter
#
# key_func=get_remote_address means "count requests per IP address"
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------------------------------------------------------------------------
# Cookie helpers
# ---------------------------------------------------------------------------
def _set_access_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        "access_token", token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=1800,
    )


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        "refresh_token", token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=604800,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/login/google")
@limiter.limit("20/minute")
def login_google(request: Request):
    """
    Redirects the browser to Google's OAuth consent screen.
    Generates a random state token to prevent CSRF attacks on the OAuth flow.
    """
    state = secrets.token_urlsafe(32)

    google_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid email profile"
        f"&state={state}"
    )

    response = RedirectResponse(google_url)
    response.set_cookie(
        "oauth_state", state,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=300,
    )
    return response


@router.get("/google/callback")
@limiter.limit("20/minute")
async def google_callback(
    request: Request,
    service: AuthService = Depends(get_auth_service),
):
    """
    Handles the redirect back from Google after the user grants consent.
    Verifies the state cookie, exchanges the code for tokens, fetches
    the user profile, and sets JWT cookies.
    """
    # CSRF check
    state_cookie = request.cookies.get("oauth_state")
    state_param = request.query_params.get("state")

    if not state_cookie or not state_param:
        raise HTTPException(400, "Missing OAuth state parameter")

    if not secrets.compare_digest(state_cookie, state_param):
        raise HTTPException(400, "OAuth state mismatch — possible CSRF attempt")

    code = request.query_params.get("code")
    if not code:
        raise HTTPException(400, "Authorization code missing from callback")

    try:
        async with httpx.AsyncClient() as client:

            token_res = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
                timeout=10,
            )

            if token_res.status_code != 200:
                logger.error(f"[Callback] Token exchange failed: {token_res.text}")
                raise HTTPException(400, "Failed to exchange authorization code with Google")

            token_json = token_res.json()
            google_access_token = token_json.get("access_token")

            if not google_access_token:
                raise HTTPException(400, "Google token response did not contain an access_token")

            user_res = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {google_access_token}"},
                timeout=10,
            )

            if user_res.status_code != 200:
                logger.error(f"[Callback] Userinfo fetch failed: {user_res.text}")
                raise HTTPException(400, "Failed to fetch user profile from Google")

            user_info = user_res.json()

            print("user_info from google is",user_info)

        access_token, refresh_token = service.google_login(user_info)

        response = RedirectResponse(FRONTEND_URL)
        _set_access_cookie(response, access_token)
        _set_refresh_cookie(response, refresh_token)
        response.delete_cookie("oauth_state")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[Callback] Unexpected error: {e}")
        raise HTTPException(500, "Google authentication failed")


@router.post("/refresh")
@limiter.limit("30/minute")
def refresh(request: Request, service: AuthService = Depends(get_auth_service)):
    """
    Issues a new access token using the refresh token cookie.
    Checks the token's jti against the SQL blocklist before issuing.
    """
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(401, "Missing refresh token")

    new_access_token = service.refresh_access_token(refresh_token)

    response = JSONResponse({"message": "Token refreshed"})
    _set_access_cookie(response, new_access_token)
    return response


@router.post("/logout")
def logout(request: Request, service: AuthService = Depends(get_auth_service)):
    """
    Revokes the refresh token by inserting its jti into the SQL blocklist,
    then clears both auth cookies. Safe to call multiple times.
    """
    refresh_token = request.cookies.get("refresh_token")
    service.logout(refresh_token)

    response = JSONResponse({"message": "Logged out"})
    _clear_auth_cookies(response)
    return response


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {
        "id": user["sub"],
        "email": user["email"],
        "roles": user["roles"]
    }



@router.get("/admin-only")
def admin_only(user=Depends(require_role("Admin"))):
    return {
        "message": "Welcome, Admin",
        "user_id": user.get("sub"),
    }

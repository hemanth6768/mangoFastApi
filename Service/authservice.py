from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timezone
 
import jwt
 
from Repository.authrepository import AuthRepository
from models.user import User
from core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from core.logger import logger
 
 
class AuthService:
 
    def __init__(self, repo: AuthRepository):
        self.repo = repo
 
    # -------------------------------------------------------------------------
    # Google OAuth login / auto-registration
    # -------------------------------------------------------------------------
 
    def google_login(self, user_info: dict) -> tuple[str, str]:
        """
        Finds or creates a user from the Google userinfo payload, then issues
        a fresh access + refresh token pair.
 
        Raises HTTPException on any validation or DB failure.
        """
        try:
            email = user_info.get("email")
            if not email:
                raise HTTPException(400, "Email not present in Google userinfo")
 
            # Google can return an unverified email in edge cases — reject it.
            if not user_info.get("verified_email", False):
                raise HTTPException(400, "Google email address is not verified")
 
            user = self.repo.get_user_by_email(email)
 
            if not user:
                logger.info(f"[AuthService] First-time Google login, creating user: {email}")
                user = self._create_google_user(user_info, email)
 
            # timezone-aware timestamp — datetime.utcnow() is deprecated in 3.12
            user.last_login_at = datetime.now(timezone.utc)
 
            # commit() lives here in the service, not scattered in the repo
            self.repo.commit()
 
            roles = self.repo.get_user_roles(user.id)
 
            access_token = create_access_token({
                "sub": str(user.id),
                "email": user.email,
                "roles": roles,
            })
            refresh_token = create_refresh_token({
                "sub": str(user.id),
            })
 
            return access_token, refresh_token
 
        except HTTPException:
            # Let intentional HTTP errors pass through unchanged
            self.repo.rollback()
            raise
 
        except IntegrityError:
            # Two concurrent first-time logins for the same email — the loser
            # rolls back and re-fetches the row that the winner committed.
            self.repo.rollback()
            logger.warning(f"[AuthService] Race condition on user creation for {email!r}, retrying fetch")
            user = self.repo.get_user_by_email(email)
            if not user:
                raise HTTPException(500, "User creation conflict — please retry")
            roles = self.repo.get_user_roles(user.id)
            access_token = create_access_token({"sub": str(user.id), "email": user.email, "roles": roles})
            refresh_token = create_refresh_token({"sub": str(user.id)})
            return access_token, refresh_token
 
        except SQLAlchemyError as e:
            self.repo.rollback()
            logger.error(f"[AuthService] DB error during google_login: {e}")
            raise HTTPException(500, "Database error")
 
        except Exception as e:
            self.repo.rollback()
            logger.exception(f"[AuthService] Unexpected error during google_login: {e}")
            raise
 
    # -------------------------------------------------------------------------
    # Token refresh
    # -------------------------------------------------------------------------
 
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Validates the refresh token, checks it has not been revoked (SQL
        blocklist), then issues a new access token.
 
        Does NOT rotate the refresh token — add rotation here if desired.
        """
        try:
            payload = verify_refresh_token(refresh_token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Refresh token has expired — please log in again")
        except jwt.PyJWTError:
            raise HTTPException(401, "Invalid refresh token")
 
        jti = payload.get("jti")
        if not jti:
            raise HTTPException(401, "Malformed refresh token — missing jti")
 
        if self.repo.is_jti_blocked(jti):
            raise HTTPException(401, "Refresh token has been revoked")
 
        new_access_token = create_access_token({"sub": payload["sub"]})
        return new_access_token
 
    # -------------------------------------------------------------------------
    # Logout
    # -------------------------------------------------------------------------
 
    def logout(self, refresh_token: str | None) -> None:
        """
        Revokes the refresh token by adding its jti to the SQL blocklist.
        Safe to call even when no token is present (no-op).
        """
        if not refresh_token:
            return
 
        try:
            payload = verify_refresh_token(refresh_token)
            jti = payload.get("jti")
            if jti:
                self.repo.block_jti(jti)
                self.repo.commit()
                logger.info(f"[AuthService] Revoked jti={jti} for sub={payload.get('sub')}")
        except jwt.PyJWTError:
            # Token is already invalid — nothing to revoke, not an error
            logger.debug("[AuthService] logout called with an already-invalid token, ignoring")
 
        except SQLAlchemyError as e:
            self.repo.rollback()
            logger.error(f"[AuthService] DB error during logout: {e}")
            raise HTTPException(500, "Could not complete logout")
 
    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------
 
    def _create_google_user(self, user_info: dict, email: str) -> User:
        """
        Creates the User row and assigns the default 'User' role.
        All writes use flush() so they are part of the caller's transaction.
        """
        user = User(
            email=email,
            first_name=user_info.get("given_name"),
            last_name=user_info.get("family_name"),
            provider="google",
            is_verified=True,
        )
        self.repo.create_user(user)
 
        role = self.repo.get_role_by_name("User")
        if not role:
            raise HTTPException(500, "Default 'User' role not found — check seed data")
 
        self.repo.assign_role(user.id, role.id)
        return user
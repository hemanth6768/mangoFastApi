from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
 
from models.user import User
from models.role import Role
from models.userrole import UserRole
from models.token_blocklist import TokenBlocklist
 
 
class AuthRepository:
 
    def __init__(self, db: Session):
        self.db = db
 
    # -------------------------------------------------------------------------
    # User
    # -------------------------------------------------------------------------
 
    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()
 
    def create_user(self, user: User) -> User:
        """
        Adds and flushes the user so that user.id is populated within the
        current transaction.  Does NOT commit — the service layer calls
        commit() explicitly after all related inserts are done.
        """
        self.db.add(user)
        self.db.flush()
        return user
 
    # -------------------------------------------------------------------------
    # Roles
    # -------------------------------------------------------------------------
 
    def get_role_by_name(self, name: str) -> Role | None:
        return self.db.query(Role).filter(Role.name == name).first()
 
    def assign_role(self, user_id: int, role_id: int) -> None:
        self.db.add(UserRole(user_id=user_id, role_id=role_id))
        self.db.flush()
 
    def get_user_roles(self, user_id: int) -> list[str]:
        roles = (
            self.db.query(Role.name)
            .join(UserRole, Role.id == UserRole.role_id)
            .filter(UserRole.user_id == user_id)
            .all()
        )
        return [r[0] for r in roles]
 
    # -------------------------------------------------------------------------
    # Token blocklist  (SQL-based revocation — no Redis required)
    # -------------------------------------------------------------------------
 
    def is_jti_blocked(self, jti: str) -> bool:
        """Returns True if this refresh token jti has been revoked."""
        return (
            self.db.query(TokenBlocklist)
            .filter(TokenBlocklist.jti == jti)
            .first()
        ) is not None
 
    def block_jti(self, jti: str) -> None:
        """
        Adds the jti to the blocklist so this refresh token can never be
        reused after logout or rotation.
        Uses merge() to silently handle duplicate inserts (idempotent logout).
        """
        entry = TokenBlocklist(jti=jti)
        self.db.add(entry)
        self.db.flush()
 
    # -------------------------------------------------------------------------
    # Transaction control  (called by the service layer, not internally)
    # -------------------------------------------------------------------------
 
    def commit(self) -> None:
        self.db.commit()
 
    def rollback(self) -> None:
        self.db.rollback()
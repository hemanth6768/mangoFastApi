"""
models/token_blocklist.py
 
SQL table for refresh token revocation.
Each row stores one revoked jti (JWT ID).
 
Migration note — add to your Alembic migration:
 
    op.create_table(
        "token_blocklist",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("jti", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
 
Cleanup:  rows older than REFRESH_TOKEN_EXPIRE_DAYS (7 days) are safe to
delete — the token they represent is already expired by then.  Run a
periodic SQL DELETE or a lightweight cron:
 
    DELETE FROM token_blocklist
    WHERE revoked_at < NOW() - INTERVAL '7 days';
"""
 
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from Database.database import Base
 
 
class TokenBlocklist(Base):
    __tablename__ = "token_blocklist"
 
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(64), unique=True, nullable=False, index=True)
    revoked_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
 
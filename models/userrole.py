from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from Database.database import Base


class UserRole(Base):

    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    role_id = Column(Integer, ForeignKey("roles.id"))

    assigned_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="roles")
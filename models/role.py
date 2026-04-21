from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from Database.database import Base


class Role(Base):

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)

    name = Column(String(100), unique=True)

    description = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    permissions = relationship("RolePermission", back_populates="role")
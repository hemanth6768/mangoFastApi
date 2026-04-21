from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from Database.database import Base


class Permission(Base):

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)

    name = Column(String(150), unique=True)

    description = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    roles = relationship("RolePermission", back_populates="permission")

    
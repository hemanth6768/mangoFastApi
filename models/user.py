from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from Database.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    email = Column(String(255), unique=True, nullable=False, index=True)

    password_hash = Column(String(255), nullable=True)

    first_name = Column(String(100))
    last_name = Column(String(100))

    provider = Column(String(50), default="local")

    is_active = Column(Boolean, default=True)

    is_verified = Column(Boolean, default=False)

    last_login_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow)

    roles = relationship("UserRole", back_populates="user")

    orders = relationship("Order", back_populates="user")

    addresses = relationship("UserAddress", back_populates="user")
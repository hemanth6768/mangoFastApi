import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime,Integer
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from Database.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    customer_name = Column(String(200), nullable=False)
    customer_email = Column(String(200), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    customer_address = Column(String(500), nullable=False)
    customer_appartment_name = Column(String(200), nullable=True)
    nearby_area = Column(String(200), nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
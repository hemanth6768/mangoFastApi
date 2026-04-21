from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from Database.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    # ✅ ADD THESE TWO (CRITICAL FIX)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    address_id = Column(Integer, ForeignKey("user_addresses.id"), nullable=True)

    customer_name = Column(String(200), nullable=False)
    customer_email = Column(String(200), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    customer_address = Column(String(500), nullable=False)
    customer_appartment_name = Column(String(200), nullable=True)
    nearby_area = Column(String(200), nullable=True)

    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ ADD THESE RELATIONSHIPS
    user = relationship("User", back_populates="orders")
    address = relationship("UserAddress", back_populates="orders")

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
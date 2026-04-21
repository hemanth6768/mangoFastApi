from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from Database.database import Base


class UserAddress(Base):
    __tablename__ = "user_addresses"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    label = Column(String(50), nullable=True)           # "Home", "Office"

    customer_name = Column(String(200), nullable=False)
    customer_phone = Column(String(20), nullable=False)

    apartment_name = Column(String(200), nullable=True)

    address = Column(Text, nullable=False)
    nearby_area = Column(String(200), nullable=True)

    is_default = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="addresses")

    orders = relationship(
        "Order",
        back_populates="address"
    )
import uuid
from sqlalchemy import Column, String , Integer
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from Database.database import Base   # adjust import if needed


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String(100), nullable=True)

    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan"
    )

    @property
    def total_price(self):
        return sum(item.price * item.quantity for item in self.items)
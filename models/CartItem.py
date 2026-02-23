import uuid
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from Database.database import Base   # adjust import if needed


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)

    cart_id = Column(
        Integer,
        ForeignKey("carts.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    product_name = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    image_url = Column(String(500))
    quantity = Column(Integer, nullable=False)

    cart = relationship("Cart", back_populates="items")
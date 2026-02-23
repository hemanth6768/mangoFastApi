import uuid
from sqlalchemy import Column, String, Numeric,Integer
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from Database.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
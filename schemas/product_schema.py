from pydantic import BaseModel
from decimal import Decimal


# -----------------------------
# Base Schema (Common Fields)
# -----------------------------
class ProductBase(BaseModel):
    name: str
    price: Decimal
    description: str | None = None
    image_url: str | None = None


# -----------------------------
# Update Schema (For PATCH)
# -----------------------------
class ProductUpdate(BaseModel):
    name: str | None = None
    price: Decimal | None = None
    description: str | None = None
    image_url: str | None = None


# -----------------------------
# Create Schema (For POST)
# -----------------------------
class ProductCreate(ProductBase):
    pass


# -----------------------------
# Response Schema (For GET)
# -----------------------------
class ProductResponse(ProductBase):
    id: int   # ✅ changed from UUID to int

    class Config:
        from_attributes = True
from pydantic import BaseModel
from decimal import Decimal
from typing import List
from datetime import datetime
from enum import Enum

class OrderItemRequest(BaseModel):
    product_id: int
    product_name: str
    price: Decimal
    quantity: int


class CustomerInfo(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    nearby_area: str
    appartment_name: str
    nearby_area: str



class OrderRequest(BaseModel):
    customer_info: CustomerInfo
    items: List[OrderItemRequest]
    total_amount: Decimal

class OrderStatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    packed = "packed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatusEnum

class OrderResponse(BaseModel):
    id: int
    status: str
    estimated_delivery: datetime
    total_amount: Decimal
    message: str

    class Config:
        from_attributes = True


class OrderItemAdminResponse(BaseModel):
    product_name: str
    quantity: int

    class Config:
        from_attributes = True


class OrderAdminResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    customer_phone: str
    customer_address: str
    customer_appartment_name: str
    total_amount: Decimal
    status: str
    created_at: datetime
    items: List[OrderItemAdminResponse]

    class Config:
        from_attributes = True
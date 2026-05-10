from pydantic import BaseModel, Field, AliasChoices
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from enum import Enum


# ─── Request Schemas ──────────────────────────────────────────────────────────

class OrderItemRequest(BaseModel):
    product_id: int = Field(validation_alias=AliasChoices("productId", "product_id"))
    quantity: int

    model_config = {"populate_by_name": True}


class CustomerInfo(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    nearby_area: str = Field(
        default="",
        validation_alias=AliasChoices("nearbyArea", "nearby_area")
    )
    appartment_name: str = Field(
        default="",
        validation_alias=AliasChoices("appartmentname", "appartment_name", "appartmentName")
    )
    label: Optional[str] = None

    model_config = {"populate_by_name": True}


class OrderRequest(BaseModel):
    user_id: Optional[int] = Field(None, validation_alias=AliasChoices("userId", "user_id"))
    address_id: Optional[int] = Field(None, validation_alias=AliasChoices("addressId", "address_id"))
    customer_info: CustomerInfo = Field(
        validation_alias=AliasChoices("customerInfo", "customer_info")
    )
    items: List[OrderItemRequest]

    model_config = {"populate_by_name": True}


class OrderStatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    packed = "packed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatusEnum
    delivered_by: Optional[str] = None  # optionally assign delivery person on status change


class AssignDeliveryPersonRequest(BaseModel):
    delivered_by: str


# ─── Response Schemas ─────────────────────────────────────────────────────────

class OrderResponse(BaseModel):
    order_id: int
    status: str
    estimated_delivery: datetime
    total_amount: Decimal
    message: str

    class Config:
        from_attributes = True


class OrderItemAdminResponse(BaseModel):
    product_name: str
    quantity: int
    price: Decimal

    class Config:
        from_attributes = True


class OrderAdminResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    customer_phone: str
    customer_address: str
    customer_appartment_name: Optional[str]
    nearby_area: Optional[str]
    total_amount: Decimal
    status: str
    created_at: datetime
    delivered_by: Optional[str]
    items: List[OrderItemAdminResponse]

    class Config:
        from_attributes = True


class AddressPrefillResponse(BaseModel):
    id: int
    label: Optional[str]
    customer_name: str
    customer_phone: str
    address: str
    apartment_name: Optional[str]
    nearby_area: Optional[str]
    is_default: bool

    class Config:
        from_attributes = True


class OrderHistoryItemResponse(BaseModel):
    id: int
    total_amount: Decimal
    status: str
    created_at: datetime
    nearby_area: Optional[str]
    customer_address: str
    customer_appartment_name: Optional[str]
    delivered_by: Optional[str]
    items: List[OrderItemAdminResponse]

    class Config:
        from_attributes = True


# ─── Admin Analytics Schemas ──────────────────────────────────────────────────

class RevenueResponse(BaseModel):
    total_revenue: Decimal
    today_revenue: Decimal
    total_orders: int
    today_orders: int

    class Config:
        from_attributes = True


class ProductSalesResponse(BaseModel):
    product_id: int
    product_name: str
    total_quantity_sold: int
    total_revenue: Decimal

    class Config:
        from_attributes = True


class OrderStatusSummaryResponse(BaseModel):
    status: str
    order_count: int
    total_revenue: Decimal

    class Config:
        from_attributes = True


class DailyRevenueResponse(BaseModel):
    date: str
    order_count: int
    total_revenue: Decimal

    class Config:
        from_attributes = True


# ─── Delivery Person Schemas ──────────────────────────────────────────────────

class DeliveryPersonSummaryResponse(BaseModel):
    delivered_by: str
    total_orders: int
    total_revenue: Decimal

    class Config:
        from_attributes = True


class DeliveryPersonOrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_phone: str
    customer_address: str
    customer_appartment_name: Optional[str]
    nearby_area: Optional[str]
    total_amount: Decimal
    status: str
    created_at: datetime
    delivered_by: Optional[str]
    items: List[OrderItemAdminResponse]

    class Config:
        from_attributes = True

class DeliveryPersonProductBreakdownResponse(BaseModel):
    product_name: str
    total_quantity: int
    total_revenue: Decimal

    class Config:
        from_attributes = True


class DeliveryPersonDetailResponse(BaseModel):
    delivered_by: str
    total_orders: int
    total_revenue: Decimal
    products: List[DeliveryPersonProductBreakdownResponse]

    class Config:
        from_attributes = True
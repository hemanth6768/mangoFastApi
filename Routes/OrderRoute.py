from fastapi import Depends, APIRouter, Query
from Database.database import get_db
from schemas.order_schema import (
    OrderRequest, OrderResponse, OrderAdminResponse,
    OrderStatusUpdateRequest, OrderStatusEnum,
    AddressPrefillResponse, RevenueResponse,
    ProductSalesResponse, OrderStatusSummaryResponse,
    DailyRevenueResponse,OrderHistoryItemResponse
)
from Service import order_service
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

router = APIRouter(prefix="/Orders", tags=["Orders"])


# ─── Checkout ─────────────────────────────────────────────────────────────────

@router.post("/checkout", response_model=OrderResponse)
def checkout(order: OrderRequest, db: Session = Depends(get_db)):
    return order_service.ordercheckout_service(order, db)


# ─── Address ──────────────────────────────────────────────────────────────────

@router.get("/addresses/prefill/{user_id}", response_model=AddressPrefillResponse)
def get_prefill_address(user_id: int, db: Session = Depends(get_db)):
    return order_service.get_prefill_address_service(user_id, db)


@router.get("/addresses/all/{user_id}", response_model=List[AddressPrefillResponse])
def get_all_addresses(user_id: int, db: Session = Depends(get_db)):
    return order_service.get_all_addresses_service(user_id, db)


# ─── Admin Orders ─────────────────────────────────────────────────────────────

@router.get("/admin/allorders", response_model=List[OrderAdminResponse])
def get_all_orders(db: Session = Depends(get_db)):
    return order_service.get_all_orders_with_items_service(db)


@router.get("/admin/orders", response_model=List[OrderAdminResponse])
def get_filtered_orders(
    status: Optional[OrderStatusEnum] = Query(None, description="Filter by order status"),
    from_date: Optional[date] = Query(None, description="From date YYYY-MM-DD"),
    to_date: Optional[date] = Query(None, description="To date YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    return order_service.get_filtered_orders_service(
        db=db,
        status=status.value if status else None,
        from_date=from_date,
        to_date=to_date,
    )


@router.put("/{order_id}/status", response_model=OrderAdminResponse)
def update_order_status(
    order_id: int,
    status_request: OrderStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    return order_service.update_order_status_service(order_id, status_request, db)


# ─── Admin Analytics ──────────────────────────────────────────────────────────

@router.get("/admin/revenue", response_model=RevenueResponse)
def get_revenue_summary(db: Session = Depends(get_db)):
    """Total revenue, today revenue, total orders, today orders"""
    return order_service.get_revenue_summary_service(db)


@router.get("/admin/product-sales", response_model=List[ProductSalesResponse])
def get_product_sales(db: Session = Depends(get_db)):
    """Per product — total quantity sold and revenue generated"""
    return order_service.get_product_sales_summary_service(db)


@router.get("/admin/status-summary", response_model=List[OrderStatusSummaryResponse])
def get_status_summary(db: Session = Depends(get_db)):
    """Order count and revenue grouped by status"""
    return order_service.get_order_status_summary_service(db)


@router.get("/admin/daily-revenue", response_model=List[DailyRevenueResponse])
def get_daily_revenue(
    from_date: Optional[date] = Query(None, description="From date YYYY-MM-DD"),
    to_date: Optional[date] = Query(None, description="To date YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """Day by day revenue — optionally filtered by date range"""
    return order_service.get_daily_revenue_service(db, from_date, to_date)



@router.get("/myorders/{user_id}", response_model=List[OrderHistoryItemResponse])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    """Order history for a specific user"""
    return order_service.get_orders_by_user_service(user_id, db)
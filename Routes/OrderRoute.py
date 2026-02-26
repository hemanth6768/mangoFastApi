from Database.database import get_db
from fastapi import FastAPI,Depends ,APIRouter
from sqlalchemy.orm import Session
from schemas.order_schema import OrderItemRequest,OrderRequest,OrderResponse,CustomerInfo,OrderAdminResponse
from Service import order_service
from schemas.order_schema import OrderStatusUpdateRequest,OrderStatusEnum
from typing import List

router = APIRouter(
    prefix="/Orders",
    tags=["Orders"]
)


@router.post("/checkout", response_model= OrderResponse)

def checkout(order:OrderRequest, db: Session = Depends(get_db)):
    return order_service.ordercheckout_service(order,db)

@router.get("/admin/allorders", response_model=list[OrderAdminResponse])
def get_all_orders(db: Session = Depends(get_db)):
    return order_service.get_all_orders_with_items_service(db)


@router.put("/{order_id}/status", response_model=OrderAdminResponse)
def update_order_status(
    order_id: int,
    status_request: OrderStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    return order_service.update_order_status_service(order_id, status_request, db)
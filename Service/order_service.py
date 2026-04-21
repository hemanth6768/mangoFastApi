from sqlalchemy.orm import Session
from Repository import order_repository
from datetime import date
from typing import Optional


def ordercheckout_service(order, db: Session):
    return order_repository.create_order(order, db)


def get_prefill_address_service(user_id: int, db: Session):
    return order_repository.get_prefill_address(user_id, db)


def get_all_addresses_service(user_id: int, db: Session):
    return order_repository.get_all_addresses(user_id, db)


def get_all_orders_with_items_service(db: Session):
    return order_repository.get_all_orders_with_items(db)


def get_filtered_orders_service(
    db: Session,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
):
    return order_repository.get_filtered_orders(
        db=db,
        status=status,
        from_date=from_date,
        to_date=to_date,
    )


def update_order_status_service(order_id: int, status_request, db: Session):
    return order_repository.update_order_status(order_id, status_request.status, db)


def get_revenue_summary_service(db: Session):
    return order_repository.get_revenue_summary(db)


def get_product_sales_summary_service(db: Session):
    return order_repository.get_product_sales_summary(db)


def get_order_status_summary_service(db: Session):
    return order_repository.get_order_status_summary(db)


def get_daily_revenue_service(
    db: Session,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
):
    return order_repository.get_daily_revenue(db, from_date, to_date)


def get_orders_by_user_service(user_id: int, db: Session):
    return order_repository.get_orders_by_user(user_id, db)
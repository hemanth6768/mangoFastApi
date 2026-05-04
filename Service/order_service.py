from sqlalchemy.orm import Session
from Repository import order_repository
from datetime import date
from typing import Optional


# ─── Checkout ─────────────────────────────────────────────────────────────────

def ordercheckout_service(order, db: Session):
    return order_repository.create_order(order, db)


# ─── Address ──────────────────────────────────────────────────────────────────

def get_prefill_address_service(user_id: int, db: Session):
    return order_repository.get_prefill_address(user_id, db)


def get_all_addresses_service(user_id: int, db: Session):
    return order_repository.get_all_addresses(user_id, db)


# ─── Admin Orders ─────────────────────────────────────────────────────────────

def get_all_orders_with_items_service(db: Session):
    return order_repository.get_all_orders_with_items(db)


def get_filtered_orders_service(
    db: Session,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    delivered_by: Optional[str] = None,
):
    return order_repository.get_filtered_orders(
        db=db,
        status=status,
        from_date=from_date,
        to_date=to_date,
        delivered_by=delivered_by,
    )


def update_order_status_service(order_id: int, status_request, db: Session):
    return order_repository.update_order_status(
        order_id,
        status_request.status,
        status_request.delivered_by,
        db,
    )


# ─── Delivery Person ──────────────────────────────────────────────────────────

def assign_delivery_person_service(order_id: int, delivered_by: str, db: Session):
    return order_repository.assign_delivery_person(order_id, delivered_by, db)


def get_delivery_person_summary_service(db: Session):
    return order_repository.get_delivery_person_summary(db)


def get_orders_by_delivery_person_service(
    delivered_by: str,
    db: Session,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
):
    return order_repository.get_orders_by_delivery_person(
        delivered_by, db, from_date, to_date
    )


def get_all_delivery_persons_service(db: Session):
    return order_repository.get_all_delivery_persons(db)


# ─── Admin Analytics ──────────────────────────────────────────────────────────

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
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, cast, Date
from models.Order import Order
from models.OrderItem import OrderItem
from models.Product import Product
from models.useraddress import UserAddress
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone, date, time
from typing import Optional
from decimal import Decimal


# ─── Checkout ─────────────────────────────────────────────────────────────────

def create_order(order_request, db: Session):
    try:
        customer = order_request.customer_info
        user_id = order_request.user_id
        address_id = None

        # ── 1. Handle address ─────────────────────────────────────────
        if user_id:
            existing_address = (
                db.query(UserAddress)
                .filter(UserAddress.user_id == user_id)
                .order_by(UserAddress.is_default.desc(), UserAddress.created_at.desc())
                .first()
            )

            if existing_address:
                address_id = existing_address.id
            else:
                new_address = UserAddress(
                    user_id=user_id,
                    label=customer.label or "Home",
                    customer_name=customer.name,
                    customer_phone=customer.phone,
                    apartment_name=customer.appartment_name or None,
                    address=customer.address,
                    nearby_area=customer.nearby_area or None,
                    is_default=True,
                )
                db.add(new_address)
                db.flush()
                address_id = new_address.id

        # ── 2. Create order ───────────────────────────────────────────
        new_order = Order(
            user_id=user_id,
            address_id=address_id,
            customer_name=customer.name,
            customer_email=customer.email,
            customer_phone=customer.phone,
            customer_address=customer.address,
            customer_appartment_name=customer.appartment_name,
            nearby_area=customer.nearby_area,
            status="pending",
            delivered_by=None,          # always null at order creation
            created_at=datetime.now(timezone.utc),
            total_amount=0,
        )

        db.add(new_order)
        db.flush()

        # ── 3. Calculate total from DB ────────────────────────────────
        total_amount = 0
        for item in order_request.items:
            db_product = db.get(Product, item.product_id)
            if not db_product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product {item.product_id} not found"
                )

            total_amount += db_product.price * item.quantity

            db.add(OrderItem(
                order_id=new_order.id,
                product_id=db_product.id,
                product_name=db_product.name,
                price=db_product.price,
                quantity=item.quantity,
            ))

        new_order.total_amount = total_amount
        db.commit()
        db.refresh(new_order)

        return {
            "order_id": new_order.id,
            "status": new_order.status,
            "estimated_delivery": datetime.now(timezone.utc) + timedelta(days=2),
            "total_amount": total_amount,
            "message": "Order placed successfully",
        }

    except Exception as e:
        db.rollback()
        raise e


# ─── Address ──────────────────────────────────────────────────────────────────

def get_prefill_address(user_id: int, db: Session):
    address = (
        db.query(UserAddress)
        .filter(UserAddress.user_id == user_id)
        .order_by(UserAddress.is_default.desc(), UserAddress.created_at.desc())
        .first()
    )
    if not address:
        raise HTTPException(
            status_code=404,
            detail="No saved address found for this user"
        )
    return address


def get_all_addresses(user_id: int, db: Session):
    return (
        db.query(UserAddress)
        .filter(UserAddress.user_id == user_id)
        .order_by(UserAddress.is_default.desc(), UserAddress.created_at.desc())
        .all()
    )


# ─── Admin Orders ─────────────────────────────────────────────────────────────

def get_all_orders_with_items(db: Session):
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .order_by(Order.created_at.desc())
        .all()
    )


def get_filtered_orders(
    db: Session,
    status: str = None,
    from_date: date = None,
    to_date: date = None,
    delivered_by: str = None,
):
    query = db.query(Order).options(joinedload(Order.items))

    if status:
        query = query.filter(Order.status == status)

    if delivered_by:
        query = query.filter(Order.delivered_by == delivered_by)

    if from_date:
        query = query.filter(
            Order.created_at >= datetime.combine(from_date, time.min)
        )

    if to_date:
        query = query.filter(
            Order.created_at <= datetime.combine(to_date, time.max)
        )

    return query.order_by(Order.created_at.desc()).all()


def update_order_status(order_id: int, status: str, delivered_by: Optional[str], db: Session):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    if delivered_by is not None:
        order.delivered_by = delivered_by
    db.commit()
    db.refresh(order)
    return order


# ─── Delivery Person ──────────────────────────────────────────────────────────

def assign_delivery_person(order_id: int, delivered_by: str, db: Session):
    """Assign or reassign a delivery person to an order."""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.delivered_by = delivered_by
    db.commit()
    db.refresh(order)
    return order


def get_delivery_person_summary(db: Session):
    """
    Per delivery person — total delivered orders + revenue.
    Only counts status = 'delivered' with delivered_by set.
    Use this for payout calculations.
    """
    results = (
        db.query(
            Order.delivered_by,
            func.count(Order.id).label("total_orders"),
            func.sum(Order.total_amount).label("total_revenue"),
        )
        .filter(
            Order.status == "delivered",
            Order.delivered_by.isnot(None),
        )
        .group_by(Order.delivered_by)
        .order_by(func.count(Order.id).desc())
        .all()
    )

    return [
        {
            "delivered_by": r.delivered_by,
            "total_orders": r.total_orders,
            "total_revenue": r.total_revenue or 0,
        }
        for r in results
    ]


def get_orders_by_delivery_person(
    delivered_by: str,
    db: Session,
    from_date: date = None,
    to_date: date = None,
):
    """All orders assigned to a specific delivery person, with optional date filter."""
    query = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.delivered_by == delivered_by)
    )

    if from_date:
        query = query.filter(
            Order.created_at >= datetime.combine(from_date, time.min)
        )
    if to_date:
        query = query.filter(
            Order.created_at <= datetime.combine(to_date, time.max)
        )

    orders = query.order_by(Order.created_at.desc()).all()

    if not orders:
        raise HTTPException(
            status_code=404,
            detail=f"No orders found for delivery person: {delivered_by}"
        )
    return orders


def get_all_delivery_persons(db: Session):
    """Return a distinct list of all delivery person names ever assigned."""
    results = (
        db.query(Order.delivered_by)
        .filter(Order.delivered_by.isnot(None))
        .distinct()
        .order_by(Order.delivered_by)
        .all()
    )
    return [r.delivered_by for r in results]


# ─── Admin Analytics ──────────────────────────────────────────────────────────

def get_revenue_summary(db: Session):
    today = datetime.now(timezone.utc).date()

    total = db.query(
        func.count(Order.id).label("total_orders"),
        func.sum(Order.total_amount).label("total_revenue")
    ).filter(
        Order.status != "cancelled"
    ).first()

    today_data = db.query(
        func.count(Order.id).label("today_orders"),
        func.sum(Order.total_amount).label("today_revenue")
    ).filter(
        Order.status != "cancelled",
        cast(Order.created_at, Date) == today
    ).first()

    return {
        "total_revenue": total.total_revenue or 0,
        "today_revenue": today_data.today_revenue or 0,
        "total_orders": total.total_orders or 0,
        "today_orders": today_data.today_orders or 0,
    }


def get_product_sales_summary(db: Session):
    results = (
        db.query(
            OrderItem.product_id,
            OrderItem.product_name,
            func.sum(OrderItem.quantity).label("total_quantity_sold"),
            func.sum(OrderItem.price * OrderItem.quantity).label("total_revenue")
        )
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status != "cancelled")
        .group_by(OrderItem.product_id, OrderItem.product_name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .all()
    )

    return [
        {
            "product_id": r.product_id,
            "product_name": r.product_name,
            "total_quantity_sold": r.total_quantity_sold,
            "total_revenue": r.total_revenue,
        }
        for r in results
    ]


def get_order_status_summary(db: Session):
    results = (
        db.query(
            Order.status,
            func.count(Order.id).label("order_count"),
            func.sum(Order.total_amount).label("total_revenue")
        )
        .group_by(Order.status)
        .all()
    )

    return [
        {
            "status": r.status,
            "order_count": r.order_count,
            "total_revenue": r.total_revenue or 0,
        }
        for r in results
    ]


def get_daily_revenue(
    db: Session,
    from_date: date = None,
    to_date: date = None,
):
    query = (
        db.query(
            cast(Order.created_at, Date).label("date"),
            func.count(Order.id).label("order_count"),
            func.sum(Order.total_amount).label("total_revenue")
        )
        .filter(Order.status != "cancelled")
        .group_by(cast(Order.created_at, Date))
        .order_by(cast(Order.created_at, Date).desc())
    )

    if from_date:
        query = query.filter(cast(Order.created_at, Date) >= from_date)
    if to_date:
        query = query.filter(cast(Order.created_at, Date) <= to_date)

    results = query.all()

    return [
        {
            "date": str(r.date),
            "order_count": r.order_count,
            "total_revenue": r.total_revenue or 0,
        }
        for r in results
    ]


def get_orders_by_user(user_id: int, db: Session):
    orders = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )
    if not orders:
        raise HTTPException(
            status_code=404,
            detail="No orders found for this user"
        )
    return orders


def get_delivery_person_product_breakdown(
    delivered_by: str,
    db: Session,
    from_date: date = None,
    to_date: date = None,
):
    query = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(
            Order.delivered_by == delivered_by,
            Order.status == "delivered",
        )
    )

    if from_date:
        query = query.filter(Order.created_at >= datetime.combine(from_date, time.min))
    if to_date:
        query = query.filter(Order.created_at <= datetime.combine(to_date, time.max))

    orders = query.all()

    if not orders:
        raise HTTPException(
            status_code=404,
            detail=f"No delivered orders found for: {delivered_by}"
        )

    # Aggregate products in Python
    product_map = {}
    total_revenue = 0
    for order in orders:
        total_revenue += order.total_amount
        for item in order.items:
            if item.product_name not in product_map:
                product_map[item.product_name] = {"total_quantity": 0, "total_revenue": Decimal(0)}
            product_map[item.product_name]["total_quantity"] += item.quantity
            product_map[item.product_name]["total_revenue"] += item.price * item.quantity

    return {
        "delivered_by": delivered_by,
        "total_orders": len(orders),
        "total_revenue": total_revenue,
        "products": [
            {
                "product_name": name,
                "total_quantity": data["total_quantity"],
                "total_revenue": data["total_revenue"],
            }
            for name, data in sorted(product_map.items(), key=lambda x: x[1]["total_quantity"], reverse=True)
        ],
    }
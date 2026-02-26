from sqlalchemy.orm import Session,joinedload
from models.Order import Order
from fastapi import HTTPException
from datetime import datetime ,  timedelta,timezone
from models.Product import Product
from models.OrderItem import OrderItem


def create_order(order_request, db: Session):

    try:
        total_amount = 0

        new_order = Order(
            customer_name=order_request.customer_info.name,
            customer_email=order_request.customer_info.email,
            customer_phone=order_request.customer_info.phone,
            customer_address=order_request.customer_info.address,
            customer_appartment_name=order_request.customer_info.appartment_name,
            nearby_area=order_request.customer_info.nearby_area,
            status="confirmed",
            created_at=datetime.now(timezone.utc),
            total_amount=0  # 🔥 set temporary value (not None)
        )

        db.add(new_order)
        db.flush()  # get order.id without commit

        for item in order_request.items:

            db_product = db.get(Product, item.product_id)

            if not db_product:
                raise HTTPException(status_code=404, detail="Product not found")

            item_total = db_product.price * item.quantity
            total_amount += item_total

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=db_product.id,
                product_name=db_product.name,
                price=db_product.price,
                quantity=item.quantity
            )

            db.add(order_item)

        # 🔥 assign total BEFORE commit
        new_order.total_amount = total_amount

        db.commit()
        db.refresh(new_order)

        return {
            "order_id": new_order.id,
            "status": new_order.status,
            "estimated_delivery": datetime.now(timezone.utc) + timedelta(days=2),
            "total_amount": total_amount,
            "message": "Order placed successfully"
        }

    except Exception as e:
        db.rollback()
        raise e
    
def get_all_orders_with_items(db: Session):

    orders = (
        db.query(Order)
        .options(joinedload(Order.items))   # 🔥 important
        .order_by(Order.created_at.desc())
        .all()
    )

    return orders


def update_order_status(order_id: int, status: str, db: Session):

    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status

    db.commit()
    db.refresh(order)

    return order
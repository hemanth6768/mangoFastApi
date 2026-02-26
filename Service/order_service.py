
from sqlalchemy.orm import Session
from Repository import order_repository



def ordercheckout_service(order,db: Session):
    return order_repository.create_order(order,db)


def get_all_orders_with_items_service(db: Session):
    return order_repository.get_all_orders_with_items(db)

def update_order_status_service(order_id: int, status_request, db: Session):
    return order_repository.update_order_status(
        order_id,
        status_request.status,
        db
    )
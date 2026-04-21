from fastapi import Depends
from sqlalchemy.orm import Session

from Database.database import get_db
from Repository.order_repository import OrderRepository
from Service.order_service import OrderService


def get_order_repository(
    db: Session = Depends(get_db),
) -> OrderRepository:
    return OrderRepository(db)


def get_order_service(
    repo: OrderRepository = Depends(get_order_repository),
) -> OrderService:
    return OrderService(repo)
from sqlalchemy.orm import Session
from Repository import product_repository


def create_product_service(product,db:Session):
    return product_repository.create_product(product.model_dump(),db)


def getall_products_service(db: Session):
    return product_repository.getall_products(db)


def updateproduct_service(product_id: int, product, db: Session):
    return product_repository.update_product(product_id, product, db)

def productdelete_service(productid , db: Session):
    return product_repository.delete_product(productid,db)
from sqlalchemy.orm import Session 
from models.Product import Product
from fastapi import HTTPException


def create_product(Product_data: dict, db: Session ):
    db_product = Product(**Product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product



def getall_products(db: Session):
    getallproducts = db.query(Product).all()
    return getallproducts


def update_product(product_id: int, product, db: Session):

    db_product = db.get(Product, product_id)

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Only update fields sent by client
    update_data = product.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)

    return db_product










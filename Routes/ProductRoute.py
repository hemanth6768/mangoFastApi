
from schemas.product_schema import ProductCreate,ProductBase,ProductResponse,ProductUpdate
from Database.database import get_db
from fastapi import FastAPI,Depends ,APIRouter
from sqlalchemy.orm import Session

from Service import Product_service



router = APIRouter(
    prefix="/product",
    tags=["products"]
)


@router.post("/addproducts", response_model= ProductResponse)
def addproduct(product: ProductCreate, db: Session = Depends(get_db)):
    return Product_service.create_product_service(product,db)




@router.get("/getallproducts", response_model=list[ProductResponse])
def getallproducts(db: Session = Depends(get_db)):
    return Product_service.getall_products_service(db)


@router.put("/Updateproducts/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    return Product_service.updateproduct_service(product_id, product, db)



@router.delete("/deleteproduct/{product_id}")

def delete_product(product_id: int, db: Session = Depends(get_db)):
    return Product_service.productdelete_service(product_id,db)





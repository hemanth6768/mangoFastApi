from fastapi import FastAPI
from Routes.ProductRoute import router
from models import Cart,CartItem,Product,Order,OrderItem

from Database.database import Base , engine

app = FastAPI()

app.include_router(router)

Base.metadata.create_all(bind=engine)
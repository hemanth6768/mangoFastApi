from fastapi import FastAPI
from Routes.ProductRoute import router as product_route
from Routes.OrderRoute import router as order_route
from models import Cart,CartItem,Product,Order,OrderItem
from fastapi.middleware.cors import CORSMiddleware
from Database.database import Base , engine

app = FastAPI()


origins = [
    "http://localhost:8080"   # React dev
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # allowed frontend domains
    allow_credentials=True,
    allow_methods=["*"],         # GET, POST, PUT, DELETE
    allow_headers=["*"],         # all headers
)


app.include_router(product_route)
app.include_router(order_route)

Base.metadata.create_all(bind=engine)
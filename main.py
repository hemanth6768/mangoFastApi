from fastapi import FastAPI
from Routes.ProductRoute import router as product_route
from Routes.OrderRoute import router as order_route
from Routes.authroute import router as auth_route
from models import Cart,CartItem,Product,Order,OrderItem,user,userrole,useraddress,rolepermission,role,permission
from fastapi.middleware.cors import CORSMiddleware
from Database.database import Base , engine
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/Static", StaticFiles(directory="Static"), name="static")
origins = [
    "http://localhost:8081"   # React dev
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
app.include_router(auth_route)

Base.metadata.create_all(bind=engine)
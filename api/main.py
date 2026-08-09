from fastapi import FastAPI
from api.database import db

from api.routers.products import router as products_router
from api.routers.orders import router as orders_router
from api.routers.chat import router as chat_router

app = FastAPI(
    title="TechStore Backend API",
    version="1.0.0"
)

app.include_router(products_router)
app.include_router(orders_router)
app.include_router(chat_router)

@app.get(
    "/",
    tags=["System"],
    summary="API Status",
    description="Checks if the TechStore Backend API and MongoDB are running."
)

def home():
    return {
        "message": "Welcome to the TechStore Backend API!",
        "database": db.name
    }
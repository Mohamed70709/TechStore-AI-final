from fastapi import APIRouter
from bson import ObjectId

from api.schemas.order import Order
from api.database import orders_collection

router = APIRouter(tags=["Orders"])

@router.post("/orders")
def create_order(order: Order):
    result = orders_collection.insert_one(order.model_dump())

    return {
        "message": "Order created successfully",
        "id": str(result.inserted_id)
    }

@router.get("/orders")
def get_orders():
    orders = []

    for order in orders_collection.find():
        order["_id"] = str(order["_id"])
        orders.append(order)

    return orders
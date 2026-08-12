from fastapi import APIRouter, Depends
from bson import ObjectId

from api.schemas.order import Order
from api.database import orders_collection
from api.dependencies import get_current_customer

router = APIRouter(tags=["Orders"])

@router.post("/orders")
def create_order(
    order: Order,
    current_customer=Depends(get_current_customer)
):
    result = orders_collection.insert_one(order.model_dump())

    return {
        "message": "Order created successfully",
        "id": str(result.inserted_id)
    }

@router.get("/orders")
def get_orders(current_customer=Depends(get_current_customer)):
    orders = []

    for order in orders_collection.find():
        order["_id"] = str(order["_id"])
        orders.append(order)

    return orders
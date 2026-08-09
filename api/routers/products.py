from fastapi import APIRouter
from bson import ObjectId
from api.schemas.product import Product
from api.database import products_collection

router = APIRouter(tags=["Products"])

@router.post("/products")
def create_product(product: Product):
    result = products_collection.insert_one(product.model_dump())

    return {
        "message": "Product added successfully",
        "id": str(result.inserted_id)
    }
@router.get("/products")
def get_products():
    products = []

    for product in products_collection.find():
        product["_id"] = str(product["_id"])
        products.append(product)

    return products

from bson import ObjectId

@router.get("/products/{product_id}")
def get_product(product_id: str):
    product = products_collection.find_one({"_id": ObjectId(product_id)})

    if not product:
        return {"message": "Product not found"}

    product["_id"] = str(product["_id"])
    return product

@router.put("/products/{product_id}")
def update_product(product_id: str, product: Product):
    result = products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": product.model_dump()}
    )

    if result.matched_count == 0:
        return {"message": "Product not found"}

    return {"message": "Product updated successfully"}

@router.delete("/products/{product_id}")
def delete_product(product_id: str):
    result = products_collection.delete_one({"_id": ObjectId(product_id)})

    if result.deleted_count == 0:
        return {"message": "Product not found"}

    return {"message": "Product deleted successfully"}
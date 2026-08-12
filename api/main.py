from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.database import db
from api.routers.products import router as products_router
from api.routers.orders import router as orders_router
from api.routers.chat import router as chat_router
from api.routers.auth import router as auth_router
from api.routers.image import router as image_router

app = FastAPI(
    title="TechStore Backend API",
    version="1.0.0"
)


# API routers
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(image_router)


@app.get(
    "/health",
    tags=["System"],
    summary="Health Check",
    description="Checks whether the API and MongoDB are available."
)
def health():
    try:
        db.command("ping")

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception:
        return {
            "status": "unhealthy",
            "database": "disconnected"
        }

@app.get(
    "/metrics",
    tags=["System"],
    summary="Application Metrics",
    description="Returns basic TechStore application metrics."
)
def metrics():
    from api.database import (
        messages_collection,
        support_tickets_collection
    )

    return {
        "messages": messages_collection.count_documents({}),
        "support_tickets": support_tickets_collection.count_documents({}),
        "products": db["products"].count_documents({}),
        "orders": db["orders"].count_documents({})
    }

# Serve the frontend
app.mount(
    "/",
    StaticFiles(
        directory="frontend",
        html=True
    ),
    name="frontend"
)
from fastapi import APIRouter, HTTPException, status
from fastapi import APIRouter, Depends
from api.dependencies import get_current_customer

from api.auth import (
    create_access_token,
    create_customer,
    get_customer_by_email,
    verify_password,
)

from api.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED
)
def register(request: RegisterRequest):

    existing_customer = get_customer_by_email(request.email)

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists."
        )

    customer = create_customer(
        name=request.name,
        email=request.email,
        password=request.password
    )

    access_token = create_access_token(
        customer["email"],
        customer.get("role", "customer")
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": customer["name"],
        "email": customer["email"]
    }


@router.post(
    "/login",
    response_model=AuthResponse
)
def login(request: LoginRequest):

    customer = get_customer_by_email(request.email)

    if not customer:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if not verify_password(
        request.password,
        customer["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    access_token = create_access_token(
        customer["email"],
        customer.get("role", "customer")
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": customer["name"],
        "email": customer["email"]
    }
@router.get("/me")
def get_my_account(
    customer: dict = Depends(get_current_customer)
):
    return {
        "name": customer["name"],
        "email": customer["email"],
        "balance": 1000.00,
        "reports": [
            "Account is active",
            "Customer account verified"
        ]
    }
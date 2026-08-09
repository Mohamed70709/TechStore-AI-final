from pydantic import BaseModel

class Order(BaseModel):
    customer: str
    customer_email: str
    status: str
    payment: str
    total: float
    eligible_refund: bool
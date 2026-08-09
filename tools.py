from database import orders, products, tickets
from rag import retrieve_documents
from api.database import support_tickets_collection

def check_order_status(order_id):
    """
    Returns the status, payment method, and total amount
    for a given order.
    """

    order = orders.get(order_id)

    if order is None:
        return {
            "error": "Order not found."
        }

    return {
        "order_id": order_id,
        "customer": order["customer"],
        "status": order["status"],
        "payment": order["payment"],
        "total": order["total"]
    }
def search_products(keyword):
    """
    Search products by name or category.
    """

    keyword = keyword.lower()
    results = []

    for product in products:
        if (
            keyword in product["name"].lower()
            or keyword in product["category"].lower()
        ):
            results.append(product)

    if not results:
        return {
            "message": "No matching products found."
        }

    return results
def cancel_order(order_id):
    """
    Cancel an order if it is still processing.
    """

    order = orders.get(order_id)

    if order is None:
        return {
            "error": "Order not found."
        }

    if order["status"] == "Processing":
        order["status"] = "Cancelled"
        return {
            "message": f"Order {order_id} has been cancelled successfully."
        }

    if order["status"] == "Shipped":
        return {
            "message": "Sorry, shipped orders cannot be cancelled."
        }

    if order["status"] == "Delivered":
        return {
            "message": "Delivered orders cannot be cancelled."
        }

    if order["status"] == "Cancelled":
        return {
            "message": "Order is already cancelled."
        }
def check_refund_eligibility(order_id):
    """
    Check if an order is eligible for a refund.
    """

    order = orders.get(order_id)

    if order is None:
        return {
            "error": "Order not found."
        }

    if order["eligible_refund"]:
        return {
            "order_id": order_id,
            "eligible": True,
            "message": "This order is eligible for a refund."
        }

    return {
        "order_id": order_id,
        "eligible": False,
        "message": "This order is not eligible for a refund."
    }
def ticket_inquiry(ticket_id):
    """
    Check the status of an existing support ticket.
    """

    ticket = tickets.get(ticket_id)

    if ticket is None:
        return {
            "error": "Ticket not found."
        }

    return {
        "ticket_id": ticket_id,
        "customer": ticket["customer"],
        "status": ticket["status"],
        "details": ticket["details"]
    }
import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")


def send_support_email(order_id, issue):

    order = orders.get(order_id)

    if order is None:
        return {
            "error": "Order not found."
        }

    customer_email = order["customer_email"]

    params = {
        "from": "onboarding@resend.dev",
        "to": [customer_email],
        "subject": "TechStore Support Escalation",
        "html": f"""
        <h2>Support Escalation</h2>

        <p><b>Order:</b> {order_id}</p>

        <p><b>Customer:</b> {customer_email}</p>

        <p><b>Issue:</b></p>

        <p>{issue}</p>
        """
    }

    resend.Emails.send(params)

    return {
        "message": "Support email sent successfully."
    }
def search_knowledge_base(query):
    """
    Search the company knowledge base for policies, FAQs,
    warranty information, and shipping details.
    """

    results = retrieve_documents(query)

    return {
        "results": results
    }
def create_support_ticket(
    session_id,
    customer_name,
    customer_email,
    summary,
    actions_taken,
    products_mentioned,
    priority
):
    """
    Create a support ticket in MongoDB when the AI cannot resolve an issue.
    """

    # Generate a simple unique ticket ID
    count = support_tickets_collection.count_documents({})
    ticket_id = f"T{count + 1001}"

    ticket = {
        "ticket_id": ticket_id,
        "session_id": session_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "summary": summary,
        "actions_taken": actions_taken,
        "products_mentioned": products_mentioned,
        "priority": priority,
        "status": "Open"
    }

    support_tickets_collection.insert_one(ticket)

    return {
        "ticket_id": ticket_id,
        "status": "Open",
        "priority": priority,
        "message": "Support ticket created successfully."
    }
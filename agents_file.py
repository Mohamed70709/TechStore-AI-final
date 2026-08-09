import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from agents import (
    Agent,
    handoff,
    function_tool,
    OpenAIChatCompletionsModel,
    RunContextWrapper,
)

from tools import (
    search_knowledge_base,
    check_order_status,
    search_products,
    cancel_order,
    check_refund_eligibility,
    ticket_inquiry,
    send_support_email,
    create_support_ticket,
)

# -----------------------
# OpenAI Configuration
# -----------------------

load_dotenv()

AGENTS_MODEL_NAME = "gpt-5.4-mini"

_async_openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

_chat_completions_model = OpenAIChatCompletionsModel(
    model=AGENTS_MODEL_NAME,
    openai_client=_async_openai_client,
)

# -----------------------
# Tool Wrappers
# -----------------------

@function_tool
def kb_search(query: str):
    """Search the company knowledge base."""
    return search_knowledge_base(query)


@function_tool
def order_status(order_id: str):
    """Check the status of an order."""
    return check_order_status(order_id)


@function_tool
def product_search(keyword: str):
    """Search for products by keyword."""
    return search_products(keyword)


@function_tool
def cancel(order_id: str):
    """Cancel an order."""
    return cancel_order(order_id)


@function_tool
def refund(order_id: str):
    """Check refund eligibility."""
    return check_refund_eligibility(order_id)


@function_tool
def ticket(ticket_id: str):
    """Check the status of a support ticket."""
    return ticket_inquiry(ticket_id)


@function_tool
def support_email(order_id: str, issue: str):
    """Send a support email."""
    return send_support_email(order_id, issue)

@function_tool
def create_ticket(
    wrapper: RunContextWrapper,
    customer_name: str,
    customer_email: str,
    summary: str,
    actions_taken: str,
    products_mentioned: list[str],
    priority: str
):
    """Create a support ticket when an issue cannot be resolved automatically."""

    session_id = wrapper.context["session_id"]

    return create_support_ticket(
        session_id,
        customer_name,
        customer_email,
        summary,
        actions_taken,
        products_mentioned,
        priority
    )
# -----------------------
# Knowledge Agent
# -----------------------

knowledge_agent = Agent(
    name="Knowledge_Agent",
    model=_chat_completions_model,
    instructions="""
You answer customer questions about:

- return policies
- warranty
- shipping
- payment policies
- FAQs

Always use the knowledge base tool for these questions.

IMPORTANT:
The knowledge base tool returns a list called "results".
The results can contain both policy titles and the actual policy details.

You MUST read and use ALL relevant results returned by the tool.
Do not assume that only the first result is useful.

For example, if the tool returns:

["Return Policy", "Items can be returned within 30 days of delivery."]

you must use the second result to answer the customer's question.

Never say that the policy details are unavailable when the returned results contain the answer.

Do not invent information that is not present in the knowledge base.

If the request is outside your area, hand it off.
""",
    tools=[
        kb_search
    ]
)


# -----------------------
# Order Agent
# -----------------------

order_product_agent = Agent(
    name="Order_Product_Agent",
    model=_chat_completions_model,
    instructions="""
You help customers with:

- checking order status
- searching products
- cancelling orders
- refund eligibility

Always use the appropriate tool.

IMPORTANT:
- If the customer asks to find, search for, or show products, ALWAYS use the product_search tool.
- Do not ask unnecessary clarification questions when the customer provides a valid product category or keyword.
- For example, if the customer says "Find laptops", immediately call product_search with keyword "laptop".
- For order status questions, ALWAYS use order_status.
- For cancellation requests, ALWAYS use cancel.
- For refund eligibility questions, ALWAYS use refund.
- Never invent product information or order information.

If the request is outside your area, hand it off.
""",
    tools=[
        order_status,
        product_search,
        cancel,
        refund
    ]
)


# -----------------------
# Support Agent
# -----------------------

support_agent = Agent(
    name="Support_Agent",
    model=_chat_completions_model,
    instructions="""
You help customers with:

- ticket inquiries
- support emails
- damaged orders
- duplicate charges
- payment problems

Always use the appropriate tool.

If the customer asks about a support ticket, ALWAYS use the ticket tool.
Do not guess or invent ticket information.

If the request is outside your area, hand it off.
If an issue cannot be resolved automatically, create a support ticket.

When creating a support ticket, include:
- the session ID
- customer name
- customer email
- a concise summary of the conversation
- actions already taken
- products mentioned
- an appropriate priority

Use High priority for urgent issues such as serious payment problems,
fraud concerns, or major unresolved order problems.

Use Medium priority for normal unresolved customer issues.

Use Low priority for minor or non-urgent issues.

After creating the ticket, tell the customer that the issue has been
escalated and provide the ticket ID.
""",
    tools=[
        ticket,
        support_email,
        create_ticket
    ]
)


# -----------------------
# Triage Agent
# -----------------------

triage_agent = Agent(
    name="Triage_Agent",
    model=_chat_completions_model,
    instructions="""
You are TechStore's receptionist.

Decide which specialist should answer.

Never answer questions yourself.

Always hand off to the correct specialist.

Routing rules:

- Questions about return policies, warranty, shipping, payment policies, FAQs,
  or general information go to the Knowledge Agent.

- Questions about products, product searches, orders, cancellations,
  or refunds go to the Order_Product_Agent.

- Questions about support tickets, support emails, damaged orders,
  duplicate charges, or payment problems go to the Support Agent.

- Questions about information from previous conversation messages,
  customer preferences, things the customer previously said,
  or remembering something from the conversation go to the Knowledge Agent.

Examples:

"What's my favorite color?"
"Do you remember what I told you?"
"What did I say earlier?"
"Do you remember my previous question?"

These should be handed off to the Knowledge Agent.
""",
    handoffs=[
        handoff(order_product_agent),
        handoff(knowledge_agent),
        handoff(support_agent)
    ]
)
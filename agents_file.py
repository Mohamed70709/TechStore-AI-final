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
    recommend_products,
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
def product_search(
    keyword: str,
    max_price: float | None = None
):
    """
    Search products by keyword and optionally filter
    by maximum price.
    """
    return search_products(
        keyword,
        max_price
    )

@function_tool
def product_recommendation(
    budget: float,
    category: str | None = None,
    use_case: str | None = None
):
    """
    REQUIRED tool for ALL product recommendation requests.

    Use this tool whenever the customer gives a budget or asks for
    products within a price limit.

    Examples:
    - "I have $500 and need a laptop"
    - "What laptop can I get for $1500?"
    - "Recommend a phone under $900"
    - "I have $1000 for a laptop"

    The budget is the customer's MAXIMUM price.

    If no products match the budget, the tool returns a message
    explaining that no products were found. You must show that
    result to the customer and never ask them to repeat the budget.

    Arguments:
    - budget: maximum amount the customer wants to spend
    - category: product category such as laptop, phone, or accessories
    - use_case: optional intended use such as programming or gaming
    """
    return recommend_products(
        budget,
        category,
        use_case
    )

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
@function_tool
def previous_user_messages(
    ctx: RunContextWrapper[dict]
):
    """
    Returns the previous user messages from the current conversation,
    excluding the current message.
    """

    session_id = ctx.context.get("session_id")

    if not session_id:
        return {
            "messages": []
        }

    from api.database import messages_collection

    messages = list(
        messages_collection.find(
            {
                "session_id": session_id,
                "role": "user"
            },
            {
                "_id": 0,
                "content": 1
            }
        ).sort("_id", -1).limit(10)
    )

    return {
        "messages": [
            message["content"]
            for message in messages
        ]
    }
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

CONVERSATION MEMORY:

When the customer asks what they previously asked, said, or discussed,
use the previous_user_messages tool.

The tool returns previous USER messages only.

Do not count assistant messages.

Do not include the current question as a previous question.

For:
"What did I ask before?"

return the most recent message from the tool.

For:
"What did I ask before before this?"

return the second-most-recent message from the tool.

For:
"What did I ask three questions ago?"

return the third-most-recent message from the tool.

Always use the tool for questions about previous user messages.

Never say that conversation history is unavailable if the tool returns
previous messages.

Do NOT repeat the current question as the answer.

For example, if the conversation is:

User: What is your return policy?
Assistant: Items can be returned within 30 days.
User: Find laptops
Assistant: Here are the available laptops.
User: What did I ask before?

The correct answer is:

"You previously asked: 'Find laptops.'"

If the customer asks:

"What did I ask before before this?"

identify the SECOND-MOST-RECENT previous USER message.

If the customer asks:

"What did I ask three questions ago?"

identify the THIRD-MOST-RECENT previous USER message.

Always count previous USER messages backward from the current message.

Do NOT count assistant messages when determining what the customer
previously asked.

Do NOT say that you cannot access the conversation history.

Do NOT claim that you only have access to the current message.

If there is no previous user message available, say that there is no
previous conversation information available.""",

    tools=[
        kb_search,
        previous_user_messages
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
PRODUCT RECOMMENDATIONS:

- If the customer gives a budget and asks for a product recommendation,
  ALWAYS call product_recommendation.
- If the customer asks for products under a specific price, ALWAYS call
  product_recommendation.
- If the customer gives a budget together with a product category,
  ALWAYS call product_recommendation.
- Extract the numeric budget from the customer's message.
- A budget such as "$500", "$1,500", "500 dollars", or "1500 USD"
  must be treated as a numeric budget.
- Do NOT ask the customer to resend a budget that is already present
  in their message.
- Pass the customer's maximum budget to product_recommendation.
- If the customer says "laptop", use category="laptop".
- Only recommend products returned by product_recommendation.
- If the tool returns products, present them to the customer.
- If the tool returns a "No products found" message, clearly tell the
  customer that no matching products are available within that budget.
- NEVER return an empty response after calling product_recommendation.
- NEVER ask the customer to repeat a budget that was already provided.

- Do not invent product information or order information.
- Only recommend products returned by the recommendation tool.
- Respect the customer's maximum budget.
- If no matching products are available, clearly tell the customer.

If the request is outside your area, hand it off.
""",
    tools=[
        order_status,
        product_search,
        product_recommendation,
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

- checking order status
- searching products
- cancelling orders
- refund eligibility
- product recommendations

Always use the appropriate tool.

IMPORTANT:

- If the customer asks to find, search for, or show products, ALWAYS use the product_search tool.
- Do not ask unnecessary clarification questions when the customer provides a valid product category or keyword.
- For example, if the customer says "Find laptops", immediately call product_search with keyword "laptop".
- For order status questions, ALWAYS use order_status.
- For cancellation requests, ALWAYS use cancel.
- For refund eligibility questions, ALWAYS use refund.

PRODUCT RECOMMENDATIONS:

- If the customer asks for product recommendations based on a budget, category, or intended use, ALWAYS use the product_recommendation tool.
- Use the customer's stated budget as the maximum allowed price.
- Only recommend products returned by the product_recommendation tool.
- Never invent products, prices, stock, or other product information.
- If the recommendation tool returns one or more products, clearly present those products to the customer.
- If the recommendation tool returns an empty recommendations list, ALWAYS provide a normal text response explaining that no matching products were found within the customer's budget.
- NEVER return an empty response after calling product_recommendation.
- If no products match the budget, you can suggest that the customer increase the budget or choose another category.
- Always finish the response with a clear answer to the customer.

For example:

Customer:
"I have a budget of $500 and need a laptop."

If the recommendation tool returns no laptops, respond with something like:

"I couldn't find any laptops within your $500 budget. If you'd like, I can search for another category or you can increase the budget."

Do not claim that products are unavailable unless the recommendation tool returned no matching products.

OTHER RULES:

- Do not invent product information or order information.
- If the request is outside your area, hand it off.
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
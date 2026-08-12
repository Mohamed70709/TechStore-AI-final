from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import re

from agents import Runner

from agents_file import triage_agent
from api.database import messages_collection
from api.schemas.chat import ChatRequest

router = APIRouter(tags=["Chat"])


def normalize_budget_request(message: str) -> str:
    """
    Detect a budget in natural language and make it explicit
    for the AI agent.
    """

    budget = None

    # Match amounts such as:
    # $500
    # $1,500
    # 500 dollars
    # 1500 USD

    dollar_match = re.search(
        r"\$\s*([\d,]+(?:\.\d+)?)",
        message,
        re.IGNORECASE
    )

    if dollar_match:
        budget = float(dollar_match.group(1).replace(",", ""))

    if budget is None:
        number_match = re.search(
            r"\b([\d,]+(?:\.\d+)?)\s*(?:dollars?|usd)\b",
            message,
            re.IGNORECASE
        )

        if number_match:
            budget = float(
                number_match.group(1).replace(",", "")
            )

    if budget is None:
        return message

    # Detect common product categories
    category = None

    message_lower = message.lower()

    if "laptop" in message_lower or "laptops" in message_lower:
        category = "laptop"
    elif "phone" in message_lower or "phones" in message_lower:
        category = "phone"
    elif "accessor" in message_lower:
        category = "accessories"

    if category:
        return (
            f"{message}\n\n"
            f"IMPORTANT REQUEST INFORMATION:\n"
            f"The customer's maximum budget is ${budget:g}.\n"
            f"The requested product category is {category}.\n"
            f"Use product_recommendation with budget={budget:g} "
            f"and category='{category}'."
        )

    return (
        f"{message}\n\n"
        f"IMPORTANT REQUEST INFORMATION:\n"
        f"The customer's maximum budget is ${budget:g}.\n"
        f"Use the product recommendation tool with this maximum budget."
    )


@router.post("/chat")
def chat(request: ChatRequest):

    # Get previous conversation history from MongoDB
    previous_messages = list(
        messages_collection.find(
            {"session_id": request.session_id},
            {"_id": 0, "role": 1, "content": 1}
        ).sort("_id", 1)
    )

    # Build the conversation input for the Agents SDK
    agent_input = [
        {
            "role": message["role"],
            "content": message["content"]
        }
        for message in previous_messages
    ]

    # Add the current user message
    agent_input.append({
        "role": "user",
        "content": request.message
    })

    # Save user's message
    messages_collection.insert_one({
        "session_id": request.session_id,
        "role": "user",
        "content": request.message
    })

    # Run the Agents SDK with conversation history
    result = Runner.run_sync(
        starting_agent=triage_agent,
        input=agent_input,
        context={
            "session_id": request.session_id
        }
    )

    print("DEBUG AGENT OUTPUT:", repr(result.final_output), flush=True)
    print("DEBUG LAST AGENT:", result.last_agent.name, flush=True)

    # Get agent response
    reply = result.final_output

    # Save assistant response
    messages_collection.insert_one({
        "session_id": request.session_id,
        "role": "assistant",
        "content": reply
    })

    # Get complete conversation history
    history = list(
        messages_collection.find(
            {"session_id": request.session_id},
            {"_id": 0, "role": 1, "content": 1}
        ).sort("_id", 1)
    )

    return {
        "session_id": request.session_id,
        "reply": reply,
        "history": history
    }
@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):

    # Get previous conversation history from MongoDB
    previous_messages = list(
        messages_collection.find(
            {"session_id": request.session_id},
            {"_id": 0, "role": 1, "content": 1}
        ).sort("_id", 1)
    )

    # Build conversation input
    agent_input = [
        {
            "role": message["role"],
            "content": message["content"]
        }
        for message in previous_messages
    ]

    # Add current user message
    agent_input.append({
        "role": "user",
        "content": normalize_budget_request(request.message)
    })

    # Save user's message
    messages_collection.insert_one({
        "session_id": request.session_id,
        "role": "user",
        "content": request.message
    })

    print(
        "SAVED USER MESSAGE:",
        request.session_id,
        request.message,
        flush=True
    )

    async def generate():

        # Run agent in streaming mode
        result = Runner.run_streamed(
            starting_agent=triage_agent,
            input=agent_input,
            context={
                "session_id": request.session_id
            }
        )

        full_response = ""

        async for event in result.stream_events():

            print(
                "STREAM EVENT:",
                event.type,
                flush=True
            )

            # Only process actual text delta events
            if (
                event.type == "raw_response_event"
                and getattr(event.data, "type", None)
                == "response.output_text.delta"
            ):

                delta = getattr(
                    event.data,
                    "delta",
                    ""
                )

                print(
                    "STREAM DELTA:",
                    repr(delta),
                    flush=True
                )

                if delta:

                    full_response += delta

                    yield (
                        f"data: "
                        f"{json.dumps({'delta': delta})}"
                        f"\n\n"
                    )

        # Fallback:
        # If streaming did not provide text,
        # use the final agent output.
        if not full_response:

            try:
                final_output = result.final_output

                print(
                    "STREAM FALLBACK:",
                    repr(final_output),
                    flush=True
                )

                if final_output:

                    full_response = final_output

                    yield (
                        f"data: "
                        f"{json.dumps({'delta': final_output})}"
                        f"\n\n"
                    )

            except Exception as error:

                print(
                    "FINAL OUTPUT ERROR:",
                    repr(error),
                    flush=True
                )

        print(
            "STREAM: finished, response =",
            repr(full_response),
            flush=True
        )

        # Save assistant response
        messages_collection.insert_one({
            "session_id": request.session_id,
            "role": "assistant",
            "content": full_response
        })

        # Tell frontend streaming is complete
        yield (
            f"data: "
            f"{json.dumps({'done': True})}"
            f"\n\n"
        )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
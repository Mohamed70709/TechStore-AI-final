from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json

from agents import Runner

from agents_file import triage_agent
from api.database import messages_collection
from api.schemas.chat import ChatRequest

router = APIRouter(tags=["Chat"])


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

    

    # Run the Agents SDK with conversation history
    result = Runner.run_sync(
        starting_agent=triage_agent,
        input=agent_input
    )

    # Get agent response
    reply = result.final_output

    # Save user's message
    messages_collection.insert_one({
        "session_id": request.session_id,
        "role": "user",
        "content": request.message
    })

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
        "content": request.message
    })

    async def generate():

        # Run agent in streaming mode
        result = Runner.run_streamed(
            starting_agent=triage_agent,
            input=agent_input
        )

        full_response = ""

        async for event in result.stream_events():

            # We only want actual assistant text
            if (
                event.type == "raw_response_event"
                and event.data.type == "response.output_text.delta"
            ):

                delta = event.data.delta

                if delta:
                    full_response += delta

                    yield f"data: {json.dumps({'delta': delta})}\n\n"

        # Save assistant response after streaming finishes
        messages_collection.insert_one({
            "session_id": request.session_id,
            "role": "assistant",
            "content": full_response
        })

        # Tell client streaming is complete
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
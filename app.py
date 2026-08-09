import os
#import json
#import gradio as gr
from dotenv import load_dotenv
#from openai import OpenAI
#from tool_schemas import tools
from agents import Runner, set_default_openai_key
from agents_file import triage_agent


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

print("API key loaded:", api_key is not None)
print("API key prefix:", api_key[:12] if api_key else "None")
print("API key suffix:", api_key[-6:] if api_key else "None")

set_default_openai_key(api_key)


def respond(message, history):

    conversation = ""

    for user_msg, assistant_msg in history:
        conversation += f"User: {user_msg}\n"
        conversation += f"Assistant: {assistant_msg}\n"

    conversation += f"User: {message}"

    result = Runner.run_sync(
        starting_agent=triage_agent,
        input=conversation
    )

    return result.final_output

# -----------------------
# Gradio Chat Interface
# -----------------------

demo = gr.ChatInterface(
    fn=respond,
    title=" TechStore AI Customer Support",
    description="Ask about orders, products, refunds, tickets, or customer support.",
    examples=[
        "Where is order 1001?",
        "Find laptops",
        "Cancel order 1001",
        "Is order 1002 eligible for a refund?",
        "Check ticket T1001",
        "I was charged twice. Please contact support."
    ]
)

if __name__ == "__main__":
    demo.launch()
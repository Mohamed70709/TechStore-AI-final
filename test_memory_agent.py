import asyncio

from agents import Runner
from agents_file import knowledge_agent


async def main():

    history = [
        {
            "role": "user",
            "content": "My favorite color is blue."
        },
        {
            "role": "assistant",
            "content": "Got it — blue is a great color."
        },
        {
            "role": "user",
            "content": "What is my favorite color?"
        },
        {
            "role": "assistant",
            "content": "Your favorite color is blue."
        },
        {
            "role": "user",
            "content": "Do you remember my favorite color?"
        }
    ]

    result = await Runner.run(
        starting_agent=knowledge_agent,
        input=history
    )

    print("RESPONSE:")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
import asyncio

from agents import Runner
from agents_file import knowledge_agent


async def main():

    result = Runner.run_streamed(
        starting_agent=knowledge_agent,
        input="What is your return policy?"
    )

    async for event in result.stream_events():
        print("EVENT TYPE:", event.type)
        print("EVENT:", event)
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())
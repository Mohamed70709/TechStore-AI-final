import asyncio

from agents import Runner
from agents_file import knowledge_agent


async def main():
    print("Testing Knowledge Agent...")

    result = await Runner.run(
        knowledge_agent,
        "What is your return policy?"
    )

    print("\nSUCCESS!")

    print("\nFINAL RESPONSE:")
    print(result.final_output)

    print("\nNEW ITEMS:")
    for item in result.new_items:
    	print(type(item).__name__)
    	print(item)


if __name__ == "__main__":
    asyncio.run(main())
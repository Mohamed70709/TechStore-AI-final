from agents import Runner
from agents_file import triage_agent

print("Testing Agents SDK...")

try:
    result = Runner.run_sync(
        starting_agent=triage_agent,
        input="Where is order 1001?"
    )

    print("SUCCESS!")
    print("Response:")
    print(result.final_output)

except Exception as e:
    print("ERROR TYPE:", type(e).__name__)
    print("ERROR:", e)
"""Smoke test: OpenMinion Python SDK facade with the project echo config."""
from openminion import APIRuntime, Agent, tool

# 1) APIRuntime path (examples/starter/quickstart.py pattern)
runtime = APIRuntime.from_config_path(None)
try:
    result = runtime.run_turn(payload={"message": "Say hello in one short sentence."})
    print("APIRuntime run_turn OK:", str(result)[:200])
finally:
    close = getattr(runtime, "close", None)
    if callable(close):
        close()

# 2) Agent + decorated tool path (forced tool use)
@tool
def lookup(order_id: str) -> str:
    """Look up an order status by id."""
    return f"{order_id}: ready"

with Agent(tools=[lookup], forced_tools=["lookup"], session_id="smoke") as agent:
    out = agent.run("Use the lookup tool for order A123.")
    print("Agent+tool OK:", str(out)[:200])

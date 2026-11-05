"""MintLens as an OpenMinion agent.

Wraps the read-only tools from mintlens.py as OpenMinion @tool functions and
runs one agent session. The agent's job is narration and orchestration only:
every fact in a brief comes from the tools, and the verdict logic is the
deterministic one in mintlens.build_brief.

Requires a real model provider in .openminion/agents.json for a meaningful
run (the hackathon requires a model-backed run; the echo provider only
exercises plumbing). Provider is configured with:
    openminion config init --provider <name>   (see OpenMinion docs)

Usage:
    python agent.py "Research this BSC contract: 0x..."
"""

from __future__ import annotations

import sys
import time

from openminion import Agent, tool

import mintlens

SYSTEM_TASK = (
    "You are MintLens, a read-only research agent for BSC free-mint opportunities. "
    "For any contract address the user gives you, call research_contract and base your "
    "answer strictly on its output. Present: identity, Sourcify verification, free-mint "
    "path signal, market status, and the verdict with its reasons. Never invent data, "
    "never suggest sending a transaction yourself — you are read-only."
)


def _stamp(result: dict) -> dict:
    """Attach an explicit observation timestamp (dated evidence for the
    runtime's freshness verifier, which looks for an `observed_at` key)."""
    out = dict(result)
    out.setdefault(
        "observed_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )
    return out


@tool(min_scope="READ_ONLY", idempotent=True)
def research_contract(address: str) -> dict:
    """Build a full read-only research brief for a BSC contract address."""
    return _stamp(mintlens.build_brief(address))


@tool(min_scope="READ_ONLY", idempotent=True)
def check_verification(address: str) -> dict:
    """Check whether a BSC contract's source is verified on Sourcify."""
    return _stamp(mintlens.check_verification(address))


@tool(min_scope="READ_ONLY", idempotent=True)
def check_market(address: str) -> dict:
    """Check DexScreener for a BSC trading pair, price, and liquidity."""
    return _stamp(mintlens.check_market(address))


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or (
        "Research this BSC contract: 0x8b8e59c014eb3e229e043ae8f3b0d7e201d21db0"
    )
    with Agent(
        tools=[research_contract, check_verification, check_market],
        session_id="mintlens",
    ) as agent:
        result = agent.run(
            SYSTEM_TASK + "\n\nUser request: " + prompt,
            thread_id="mintlens-main",
        )
        print(result.text if hasattr(result, "text") else result)


if __name__ == "__main__":
    main()

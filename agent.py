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

No-key behaviour: if no model API key is available (OPENAI_API_KEY unset
and no local key file — see .env.example), the model layer is skipped
with a clear notice and the deterministic brief from mintlens.py is
printed instead, so a fresh checkout still runs end-to-end first-try.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

from openminion import Agent, tool

import mintlens

KEY_ENV = "OPENAI_API_KEY"
KEY_FILE = Path(__file__).parent / ".openminion" / "gemini.key"


def _ensure_provider_key() -> bool:
    """Make the configured provider key available via env, if we have one.

    Resolution order: an existing OPENAI_API_KEY in the environment, then
    the local key file .openminion/gemini.key (operator convention,
    gitignored, chmod 600). Returns True when the model layer can run.
    """
    if os.environ.get(KEY_ENV):
        return True
    try:
        key = KEY_FILE.read_text().strip()
    except Exception:  # noqa: BLE001 - no key file is a normal state
        return False
    if key:
        os.environ[KEY_ENV] = key
        return True
    return False

SYSTEM_TASK = (
    "You are MintLens, a read-only research agent for BSC free-mint opportunities. "
    "For any contract address the user gives you, call research_contract and base your "
    "answer strictly on its output. Present: identity, Sourcify verification, free-mint "
    "path signal, market status, and the verdict with its reasons. Never invent data, "
    "never suggest sending a transaction yourself — you are read-only. "
    "Always answer in English."
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
    # Reproducibility guard (FINDINGS #12): a NO_PROXY value containing
    # bracketed IPv6 entries crashes httpx before any request is made.
    if "[" in os.environ.get("NO_PROXY", ""):
        os.environ["NO_PROXY"] = "localhost,127.0.0.1"
    if not _ensure_provider_key():
        # No model key: do not crash inside the provider — say so plainly
        # and serve the deterministic brief (which never needed a model).
        print(
            "[mintlens] No model API key found (OPENAI_API_KEY is unset and "
            ".openminion/gemini.key is missing) — model layer SKIPPED; "
            "running the deterministic brief path instead."
        )
        match = re.search(r"0x[0-9a-fA-F]{40}", prompt)
        if not match:
            print(
                "The prompt contains no contract address; nothing to "
                "research without the model layer."
            )
            return
        print(json.dumps(mintlens.build_brief(match.group(0)), indent=2))
        return
    # Deterministic routing: a prompt carrying a contract address is a
    # research request, so force the umbrella research tool — small models
    # otherwise sometimes skip it or pick a granular tool, and the runtime's
    # freshness verifier then (correctly) blocks the ungrounded answer.
    forced = ["research_contract"] if re.search(r"0x[0-9a-fA-F]{40}", prompt) else None
    with Agent(
        tools=[research_contract, check_verification, check_market],
        session_id="mintlens",
        forced_tools=forced,
    ) as agent:
        result = agent.run(
            SYSTEM_TASK + "\n\nUser request: " + prompt,
            thread_id="mintlens-en",
        )
        print(result.text if hasattr(result, "text") else result)


if __name__ == "__main__":
    main()

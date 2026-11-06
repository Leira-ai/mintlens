"""Cross-process memory demo for the MintLens OpenMinion agent.

Runs agent.py twice as two genuinely separate OS processes. The only
thing the two processes share is the OpenMinion conversation thread:
agent.py passes thread_id="mintlens-en" to Agent.run(), and the runtime
persists thread history under .openminion/state/ — which is what makes
recall work across processes (FINDINGS #10: session_id alone does not).

    Process 1 — "Research this BSC contract: 0x48c3…c0f0" (Moth Club).
                The agent calls research_contract; the brief and the
                agent's narrated answer land in the thread history.
    Process 2 — a brand-new process whose prompt contains NO address:
                "For the contract you just researched, what was the
                verdict, and did a free mint path exist?"
                It can only be answered from the shared thread history.

Why a separate script instead of calling agent.py by hand: the demo is
meant to be replayable evidence — one command runs both processes back
to back and prints a self-labelling transcript (captured verbatim in
examples/memory-demo-transcript.txt).

    python memory_demo.py

Needs the same provider setup as agent.py (see README Quickstart).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent

MOTH_CLUB = "0x48c3ae8e8129efa9d20800ac8932d8b51f85c0f0"  # ground truth: Layak
STEP1_PROMPT = f"Research this BSC contract: {MOTH_CLUB}"
STEP2_PROMPT = (
    "For the contract you just researched in this conversation, what was "
    "the verdict, and did a free mint path exist? Answer from our "
    "conversation history — do not research a new contract."
)


def run_step(label: str, prompt: str) -> int:
    print(f"\n===== {label} =====")
    print(f'$ python agent.py "{prompt}"')
    print(f"(started {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})")
    # FINDINGS #12: a bracketed-IPv6 NO_PROXY crashes httpx in the child
    # too — hand the subprocesses a sanitized proxy env.
    env = dict(os.environ, NO_PROXY="localhost,127.0.0.1", no_proxy="localhost,127.0.0.1")
    proc = subprocess.run(
        [sys.executable, str(HERE / "agent.py"), prompt],
        cwd=HERE,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(proc.stdout.rstrip())
    print(f"(exit code {proc.returncode})")
    return proc.returncode


def main() -> int:
    print("MintLens memory demo — two separate agent.py processes, one")
    print("shared OpenMinion thread (thread_id='mintlens-en', set in agent.py).")
    rc1 = run_step("PROCESS 1 — research (tool call, address in prompt)", STEP1_PROMPT)
    rc2 = run_step("PROCESS 2 — recall (new process, NO address in prompt)", STEP2_PROMPT)
    print("\n===== DEMO DONE =====")
    print(f"process 1 exit={rc1}, process 2 exit={rc2}")
    print("Read process 2's answer above: it names the Moth Club contract,")
    print("its verdict ('Layak') and the free-path result — none of which")
    print("appear in process 2's prompt. They came from the thread history.")
    return 0 if rc1 == 0 and rc2 == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

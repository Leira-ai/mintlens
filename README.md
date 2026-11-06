# MintLens

A read-only research agent for BSC free-mint opportunities, built on the
[OpenMinion](https://github.com/OpenMinion/openminion) SDK for
Cortensor Hackathon #5.

Give MintLens a BSC contract address and it returns a grounded research brief:
what the contract is, whether its source is verified, whether a free
mint/claim path appears reachable, whether a market exists yet — and a
calibrated verdict (**Layak** / **Pantau** / **Hindari** — roughly
*worth it* / *watch* / *avoid*). Every fact in the brief comes from a live
read-only check; the language model only orchestrates the tools and narrates
their output.

MintLens is a miniature of a production verification pipeline used to screen
Agent-ID free mints: it never signs, never sends a transaction, and treats a
passing simulation as a *signal*, never as proof.

## Run it in 2 minutes

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) Deterministic brief — no API key, no model needed:
python mintlens.py brief 0x48c3ae8e8129efa9d20800ac8932d8b51f85c0f0
#    → Moth Club brief, verdict "Layak"
#      (sample output: examples/sample-brief-moth-club.json)

# 2) End-to-end smoke test of the same pipeline (asserts structure + verdict):
python smoke_test.py

# 3) Optional — the model-backed agent (needs a provider config + key):
openminion config init --provider openai   # creates .openminion/agents.json
cp .env.example .env                       # then put your key in .env
set -a; source .env; set +a
python agent.py "Research this BSC contract: 0x48c3ae8e8129efa9d20800ac8932d8b51f85c0f0"
```

No key handy? `python agent.py "Research 0x…"` still runs: it prints that
the model layer is skipped and serves the deterministic brief instead of
crashing. Key sources (env var, or a local key file) are documented in
[.env.example](.env.example); provider/model setup details are in the
Quickstart section below.

## How it works

```
user prompt ──► OpenMinion Agent (agent.py)
                  │  calls tools, narrates results
                  ▼
        ┌─────────────────── mintlens.py (deterministic core) ───────────────────┐
        │ research_contract(address)                                             │
        │   1. Identity        eth_call: name / symbol / totalSupply / owner   │
        │   2. Verification    Sourcify v2: match level + contract name        │
        │   3. Free-path probe value-0 eth_call simulation of 8 common         │
        │                      mint/claim methods, from TWO perspectives:      │
        │                      a fresh address AND the operator wallet         │
        │   4. Market          DexScreener: best BSC pair, price, liquidity    │
        │   5. Verdict         deterministic rules over the four checks        │
        └──────────────────────────────────────────────────────────────────────┘
```

The dual-perspective probe is the interesting part: one simulation sender
conflates three very different states — *no free path*, *free path exists*,
and *free path exists but this wallet's quota is already spent*. Probing from
both a fresh address and the operator wallet separates them. It also exposes a
whole family the generic probe cannot see: Agent-ID-gated mints revert from
any plain address, so MintLens reports "not detected" rather than "does not
exist", and never condemns a verified contract just because the probe came
back empty.

Verdict rules (deterministic, in `build_brief`):

- **Layak** — a free path passes simulation *and* the source is verified.
- **Pantau** — any single positive signal (verified source, a market, or a
  free-path signal) without the full combination.
- **Hindari** — no code at the address, or no positive signal at all.

Briefs are cached locally for 6 hours (`.mintlens_cache.json`) so repeated
questions don't re-hammer public RPCs.

## OpenMinion building blocks used

- **`Agent` facade + `@tool`** — three tools (`research_contract`,
  `check_verification`, `check_market`) wrap the deterministic core.
- **Tool policy annotations** — the tools are declared
  `@tool(min_scope="READ_ONLY", idempotent=True)`, which is what makes the
  runtime's policy engine classify them as read / no-side-effects /
  reversible. Without the annotation, a bare `@tool` defaults to a WRITE_SAFE
  scope and the run stops at an interactive confirmation prompt.
- **Pluggable provider config** (`.openminion/agents.json`) — developed
  against the `echo` provider for plumbing, then run for real on **Gemini**
  through Google's official OpenAI-compatible endpoint plugged into the
  `openai` provider slot (the SDK ships no native Gemini provider in
  0.1.18 — see FINDINGS #7). Any OpenAI-compatible provider works the same way.
- **Sessions with explicit `thread_id`** — `agent.run(..., thread_id=
  "mintlens-en")` resumes conversation history across processes;
  `session_id` alone does not (FINDINGS #10).
- **Freshness verification** — tool results are returned as structured dicts
  stamped with an `observed_at` timestamp, satisfying the runtime's
  dated-evidence requirement for time-sensitive answers (FINDINGS #11).
- **Runtime timeout tuning** — chat/API/brain turn timeouts raised in config
  for slow networks (FINDINGS, config note).

What we deliberately did **not** enable: the SDK's blockchain signing tools
and SSH tools exist in the runtime, but MintLens runs a read-only profile —
no keys, no signing, no transactions. Our three tools only perform `eth_call`
reads and public API GETs.

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install openminion==0.1.18 requests pycryptodome

# deterministic core, no model needed:
python mintlens.py brief 0x8b8e59c014eb3e229e043ae8f3b0d7e201d21db0

# agent (needs a model provider):
openminion config init --provider openai   # or openrouter / groq / ...
# edit .openminion/agents.json: set the provider's base_url + model,
# and export the key under the provider's api_key_env name, e.g.
#   export OPENAI_API_KEY=...   (a Gemini key + Google's OpenAI-compatible
#                                base_url works — see FINDINGS #7)
python agent.py "Research this BSC contract: 0x8b8e59c014eb3e229e043ae8f3b0d7e201d21db0"

# follow-up in the same thread (history resumes):
python agent.py "Which contract did I just ask about, and what was the verdict?"
```

Expected output for the example contract (Kitebots, an Agent-ID-gated NFT
collection the operator had already minted): identity read on-chain, Sourcify
*exact match*, no free path detected from a plain address (the gate is
identity-based — the brief says so), no DEX pair yet, verdict **Pantau**.

## Example run (real model, Gemini 3.1 Flash Lite)

> **Identity:** Kitebots (KITE), total supply 668, owner `0x4e9b…08dba`
> **Sourcify:** verified (exact match)
> **Free-mint path signal:** none detected — all value-0 simulations reverted
> from the test address; the path may be identity-gated
> **Market:** no BSC pair on DexScreener
> **Verdict: Pantau**

A second process then answered "which contract did I ask about, and what was
the verdict?" correctly from thread history alone.

## Demo video

[mintlens-demo.mp4](mintlens-demo.mp4) (73 seconds, in this repo) — a
walkthrough of the real product: getting set up with a model provider, the
deterministic CLI brief, a real model-backed agent run whose verdict matches
the CLI, how to read the verdict, and a second process recalling the first
one's research from thread history. Segment list and production notes are in
[DEMO.md](DEMO.md). Every terminal excerpt in the video is from an actual
2026-11-06 run.

## Safety posture

- Read-only by construction: `eth_call` simulations and public GETs only.
- The agent's system prompt forbids inventing data and forbids suggesting it
  can transact; the verdict logic is deterministic code, not model opinion.
- No API keys or wallet material in this repo; provider keys are supplied via
  environment at run time.

## Findings

Building-block notes, rough edges, and feedback for the OpenMinion team are
in [FINDINGS.md](FINDINGS.md) — 13 numbered findings from building and
running MintLens, including the ones referenced above.

## Limitations (honest list)

- Identity-gated free mints (e.g. Agent ID) under-detect: the probe can say
  "not detected", never "proven absent", for that family.
- A passing simulation is a signal, not a mint guarantee — production use
  needs the full gate (contract from the project's own site, quota reads,
  transaction preview) before anything is signed.
- Public RPC / API rate limits apply; the 6 h cache mitigates repeat checks.

# MintLens — Building Blocks Tested (draft, grows during the build)

Project: MintLens, a read-only BSC free-mint research-brief agent for Cortensor Hackathon #5.
SDK: openminion 0.1.18 (PyPI), Python venv.

## 2026-11-06 — Install + plumbing (echo provider)

Tested: installation, CLI (`config init`, `run`, `--version`), Python facade
(`APIRuntime.run_turn`, `Agent` + `@tool` + `forced_tools`), project-scoped config
(`.openminion/agents.json`).

What worked:
- `pip install openminion==0.1.18` succeeded in a fresh venv; `import openminion` reports 0.1.18.
- `openminion config init --provider echo` created the project config + local state DB.
- CLI run, `APIRuntime.run_turn`, and an `Agent` session with a run-scoped decorated tool all
  completed end-to-end under the echo provider.

Findings / rough edges:
1. Docs quickstart uses `python3.11 -m venv`, but this machine ships only Python 3.12.3
   (no `python3.11` binary). The 0.1.18 wheel installed and ran cleanly on 3.12.3 — the docs
   could state the supported range (3.11+ incl. 3.12) instead of pinning the example to 3.11.
2. Under the echo provider the output is the literal echo (`openminion: <input>`), and an
   `Agent` run with `forced_tools` returns without any visible evidence the tool was invoked —
   expected for a demo provider (readiness labels this `demo`, not `ready`), but a first-time
   SDK user cannot tell from the result object alone whether the tool ran. A `tool_invocations`
   field (even empty) on `AgentRunResult` would make plumbing tests verifiable without a
   paid provider.
3. INFO-level runtime logs (context composition metrics, lifecycle events) are printed during
   a plain `APIRuntime` run, interleaved with program output. Fine for debugging; noisy for
   embedding. (Workaround: configure logging level in the host app.)

## 2026-11-06 — MintLens tools built + first live tests

Built `mintlens.py` (contract identity via eth_call, Sourcify verification, DexScreener
market, free-path probe matrix, deterministic brief + 6h cache) and `agent.py`
(OpenMinion `Agent` with three `@tool` wrappers). Live-tested on four contracts the
operator's production scanner had already minted/claimed, so ground truth was known.

What worked:
- Identity, Sourcify, market, and cache all correct against ground truth
  (e.g. RuninAI: exact_match "FairAgentLaunchV3", live pair, price/liquidity read back).
- Ungated free mint (Moth Club): probe passes from a fresh address, fails from the
  operator wallet whose 1-per-wallet quota is spent — exactly the expected contrast.

Findings / rough edges:
4. **Simulation sender identity decides what a probe can see.** Agent-ID-gated free
   mints (Kitebots, Mossminds) revert from *any* plain EOA, fresh or operator, because
   the gate checks the caller's agent identity — a generic probe matrix silently
   under-detects this whole family. A research agent needs identity-aware reads
   (e.g. labelhash-based quota views) alongside raw simulation, and its report must
   say "not detected" rather than "does not exist". This shaped MintLens' verdict
   calibration: a Sourcify-verified contract is never judged "Hindari" solely
   because the generic probe found no free path.
5. Sourcify API v2 quirk (external API, noted for other builders): there is no
   top-level `name` field selector — requesting it returns HTTP 400; the contract
   name lives in `metadata.settings.compilationTarget`, and one `fields=metadata`
   call returns both `match` and the name.
6. Dual-perspective probing (fresh address vs operator wallet) separates three
   states a single probe conflates: no free path / free path exists / free path
   exists but this wallet's quota is spent.

## 2026-11-06 — Real provider run (Gemini) + sessions/memory

Tested: model-backed `Agent` runs with a real provider, tool calling end-to-end,
and conversation continuity across separate processes. Model: Gemini via
Google's official OpenAI-compatible endpoint, key supplied by the operator.

What worked:
- The agent called `research_contract` on its own, grounded its answer in the
  tool output (identity, Sourcify exact match, no free-path signal, no DEX pair)
  and returned the same verdict ("Pantau") as the deterministic CLI brief for
  the same contract (Kitebots) — narration layer agrees with ground truth.
- With an explicit `thread_id`, a second process recalled the previously
  researched contract and its verdict from conversation history (see #10).

Findings / rough edges:
7. **No native Gemini provider in 0.1.18.** The shipped provider set is
   OpenAI/Anthropic/OpenRouter/Groq/Cerebras/Cortensor/Ollama (+echo). A Gemini
   API key works through Google's official OpenAI-compatible endpoint
   (`https://generativelanguage.googleapis.com/v1beta/openai/`) plugged into
   the `openai` provider slot (Bearer key, `api_key_env`), including tool
   calling — but a user following the README's provider list would not find
   this path. A first-class `gemini` provider entry (or a docs note) would help.
8. **Model availability is account-age dependent (external, noted for other
   builders).** For a brand-new AI Studio key, `gemini-2.5-flash` returns 404
   "no longer available to new users", and `gemini-3.8-flash` repeatedly
   returned 503 high-demand (and >60 s stalls). `gemini-3.1-flash-lite`
   answered a trivial call in ~11 s and drove the full agent loop reliably.
   Provider defaults should be re-validated per account, not assumed.
9. **Facade `@tool` defaults gate read-only tools behind interactive
   confirmation.** A bare `@tool` lands in a WRITE_SAFE family scope, so the
   policy engine classifies it as risk `write` with `unknown` reversibility and
   requires confirmation — which silently ends a non-interactive run.
   Annotating genuinely read-only tools with
   `@tool(min_scope="READ_ONLY", idempotent=True)` yields the correct
   read/none/reversible classification. The default is safe, but the failure
   mode (run ends at a prompt nobody sees) deserves a louder signal.
10. **`session_id` alone does not resume history across processes.** Two
    `Agent` runs sharing `session_id="mintlens"` started fresh conversations.
    Passing an explicit stable `thread_id` to `Agent.run()` activates the
    runtime's explicit-thread routing and history resumes correctly across
    processes (verified by recall). This distinction is easy to miss from the
    facade API alone.
11. **Freshness verifier needs dated evidence inside tool outputs.** For
    time-sensitive questions the runtime blocks the final answer unless tool
    outputs contain one of a fixed key set (`observed_at`, `retrieved_at`,
    `published_at`, …). Returning structured dicts (not JSON strings) from
    tools and stamping them with `observed_at` satisfies it — and is good
    research hygiene anyway. Our earlier `checked_at` key was not in the set,
    which cost one failed run to diagnose.
12. **Host environment can break the SDK's HTTP stack (reproducibility note).**
    This VM's `NO_PROXY` contains bracketed IPv6 entries (`[::1]`,
    `[fd8b:…::1]`); httpx parses every `no_proxy` entry as a URL pattern and
    raises `InvalidURL: Invalid port: ':1]'` before any request — the failure
    surfaces as a generic provider error. Sanitizing `NO_PROXY` to
    `localhost,127.0.0.1` for the agent process fixes it. The SDK could
    pre-validate proxy env vars and name the culprit in the error.
    Reported upstream as
    [issue #686](https://github.com/openminion/openminion/issues/686);
    a fix with regression tests (retry construction with the bracketed
    entries rewritten to unbracketed form, plus a warning that names the
    variable and the rewritten entries) is open as
    [PR #687](https://github.com/openminion/openminion/pull/687).

Config note: default turn timeouts (chat 90 s / API 45 s) were too tight for a
slow egress path + a reasoning model; raised in `.openminion/agents.json`
(chat 300 s, API 180 s, brain 600 s).

13. **A thread can be poisoned by its own blocked replies.** After several
    freshness-verifier blocks landed in the `mintlens-main` thread history,
    later research turns on that thread stopped producing qualifying evidence
    at all (the model pattern-matched its own blocked replies and skipped the
    tool call), failing with both "missing live-data" and "missing
    exact-date" — while the identical prompt on a fresh thread passed
    immediately, with the same tools and model. Two mitigations worked:
    deterministic routing (force `research_contract` whenever the prompt
    contains a contract address) and starting the demo pair on a clean
    thread. Related: a single fresh research brief takes ~70 s of wall time
    on a slow network (16+ RPC/API calls), so slow tools plus long threads
    make verifier outcomes flaky in ways that look like model failure.
    Verifier diagnostics that name *which* action was evaluated would help.

## Building Blocks Tested (summary)

| Building block | How MintLens used it | Result |
|---|---|---|
| CLI (`config init`, `run`, `--version`) | Project scaffolding, echo smoke tests | Works; see #1–#3 |
| `APIRuntime.run_turn` | Programmatic single-turn runs | Works |
| `Agent` facade | Main agent loop with a real model (Gemini) | Works; grounded tool-grounded answers |
| `@tool` decorated tools | 3 read-only research tools | Works after policy annotation; see #9 |
| Tool policy engine (risk classification) | `min_scope="READ_ONLY"`, `idempotent=True` | Correct read/none/reversible classification |
| Provider system (pluggable) | echo → OpenAI slot → Gemini OpenAI-compatible endpoint | Works; no native Gemini provider (#7, #8) |
| Sessions / threads | `session_id` + explicit `thread_id` on `run()` | Thread routing resumes history across processes (#10) |
| Freshness verification | Structured tool outputs with `observed_at` | Answer accepted once dated evidence present (#11) |
| Runtime config (`.openminion/agents.json`) | Provider, timeouts, state paths | Works; defaults too tight for slow networks |
| Local state (sessions/memory DBs) | Persisted under `.openminion/state/` | Works |

Not enabled, by design: blockchain signing tools, SSH tools, subagents /
Handoff (planned next), typed `output_type` briefs.

## What We Learned

1. **The model is the narrator, not the oracle.** Every durable decision in
   MintLens (verdict, quota state, market state) is deterministic code over
   live reads. The LLM's job is tool orchestration and explanation. This made
   the agent's output auditable against ground truth — and it agreed.
2. **Simulation results depend on who asks.** A value-0 `eth_call` probe is a
   statement about (contract, sender, block), not about the contract alone.
   Two sender perspectives turned one ambiguous "revert" into three
   distinguishable states, and revealed an entire identity-gated mint family
   that generic tooling under-detects.
3. **Safe defaults have silent failure modes.** The SDK's conservative
   defaults (WRITE_SAFE tool scope, unknown reversibility, tight timeouts)
   are the right defaults — but each one failed *quietly* (a prompt nobody
   sees, a generic provider error, a 90 s timeout). Building with this SDK
   taught us to read the policy/verification layers early, not after the
   first confusing run.
4. **Freshness is a data-format contract.** The runtime's demand for dated
   evidence in tool outputs looked like friction; it is actually a good
   discipline. Stamping every observation with `observed_at` improved the
   research output itself, not just the verifier's mood.
5. **Provider reality is per-account.** A model listed in the catalog can be
   unavailable to a new key (404) or saturated (503). A resilient agent
   setup validates its exact model with its exact key before the demo, and
   keeps a known-good fallback (for us: a Flash Lite tier model).

## Still open
- Read-only permission profile: confirm non-allowlisted tools (blockchain signing, SSH) are unreachable from the agent's tool surface.
- Typed output for the brief schema; diagnostics/status commands.
- Subagent / Handoff building blocks with a second specialised agent.

## Update 2026-11-06 — verdict labels renamed to English

The verdict labels were originally Indonesian (Layak / Pantau / Hindari,
used in the dated entries above, which are kept as written). At the
operator's request the program's user-facing output is now English-only:
the labels are **Worth it** / **Watch** / **Avoid** (constants
`VERDICT_WORTH_IT` / `VERDICT_WATCH` / `VERDICT_AVOID` in mintlens.py).
The deterministic example outputs (`sample-brief-moth-club.json`,
`runtime-proof-moth-club.txt`, `batch-output.txt`) were regenerated live
after the rename, and the smoke test asserts the Moth Club ground-truth
verdict as "Worth it" (15/15, live brief). The cross-process memory
transcript is kept as its original capture: re-running `memory_demo.py`
that evening hit the runtime freshness verifier blocking the agent's
answers (4/4 attempts, both ground-truth contracts, cached and live
briefs alike — the same verifier behaviour as #11, and a reminder that
it is model/verifier-state dependent, not deterministic).

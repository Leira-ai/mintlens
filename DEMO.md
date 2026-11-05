# MintLens — demo video script (target 1–5 minutes)

Rendered video: `mintlens-demo.mp4` (slides rendered from this script by
`render_demo.py`; all terminal excerpts are from real runs on 2026-11-06).

| # | Slide | On screen | Sec |
|---|-------|-----------|-----|
| 1 | Title | MintLens — a read-only BSC free-mint research agent. Built on the OpenMinion SDK · Cortensor Hackathon #5 | 6 |
| 2 | Problem | Free mints appear fast; checking each contract by hand is slow and error-prone | 6 |
| 3 | Pipeline | 5 deterministic checks: identity, Sourcify, free-path probe ×2 senders, market, verdict | 8 |
| 4 | Terminal 1 | `python mintlens.py brief 0x8b8e…1db0` → JSON brief excerpt (Kitebots) | 10 |
| 5 | Terminal 2 | `python agent.py "Research this BSC contract: …"` → agent answer excerpt, verdict Pantau | 12 |
| 6 | Terminal 3 | Follow-up: "Which contract did I just ask about?" → recalled from thread history | 10 |
| 7 | Key idea | Dual-perspective probing: simulation results depend on the sender | 8 |
| 8 | Building blocks | Agent facade, @tool policy annotations, provider config, thread sessions, freshness evidence | 8 |
| 9 | Findings | 12 findings for the OpenMinion team (FINDINGS.md) — incl. no native Gemini provider, WRITE_SAFE default gate, thread_id vs session_id | 8 |
| 10 | Close | Read-only by construction. No signing. Deterministic verdicts. Repo + README | 6 |

Total ≈ 82 seconds.

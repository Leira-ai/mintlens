# MintLens — Demo Video v5 Script & Production Notes

**What changed vs v4:** v4 was a programmatic render (text cards + simulated
terminal typing, 73 s, no narration). v5 is built from **real asciinema
recordings** of the product actually running in a terminal (`.cast` files keep
the genuine byte stream and timings of each run), converted to video with a
terminal emulator renderer, with real voice narration, styled subtitles, and
the original `music_bgm.py` composition mixed under the voice.

**Target:** 2.5–3.5 minutes, 1280×720. Voice: Helio (default), English.
BGM: `music_bgm.py` (original synth composition), low under narration.

## Narration script (as synthesized)

### S1 — Hook / intro (over title card, into the live run)

Free mints on BNB Chain are a minefield. Pools that promise a free mint can
hide paid traps, fake quotas, and contracts that were never verified. MintLens
checks a contract before you ever connect a wallet. It is a read-only research
agent built on the OpenMinion SDK, created for Cortensor Hackathon number
five. Give it a contract address, and it investigates, live and on-chain, then
returns a verdict you can audit.

### S2 — Live CLI brief: Moth Club (`mintlens.py brief … --fresh`)

This is a real run, recorded live. MintLens reads the contract's identity
straight from the chain. It checks the source code on Sourcify. Then it probes
eight common free-mint methods, simulating every call with zero value, from
two different perspectives: a fresh address, and the operator's own wallet.
That distinction matters, because a path that is open to a new wallet may
already be spent for yours. Finally, it checks whether any market exists. The
verdict for Moth Club is Layak: qualified. Verified source code, and a free
mint path that passes simulation.

### S3 — Batch comparison (`mintlens.py batch … --fresh`)

MintLens can also say no. In batch mode, it compares contracts side by side,
with the evidence for every verdict on one line. Kitebots is verified too, but
no free path passed simulation, so its verdict is Pantau: monitor only. Same
checks, same honesty, whether the answer is yes or no.

### S4 — Agent + cross-process memory (`memory_demo.py`)

MintLens also runs as a conversational agent. Here, one process researches
Moth Club and narrates the findings. Then a second, completely separate
process starts. Its prompt contains no address at all. Asked what the verdict
was, it answers from the shared conversation thread: Moth Club, Layak, free
path found. That is OpenMinion's persistent memory, working across processes,
exactly as documented in our findings.

### S5 — Findings close + end card

Building MintLens surfaced thirteen documented findings about the OpenMinion
SDK: what worked, what surprised us, and what broke. One finding was a real
bug, a common proxy setting that crashed every provider call. We fixed it
upstream, with regression tests. MintLens never signs, never transacts, and
never guesses. It just does the homework, before your wallet is on the line.
The code is public. Thank you for watching.

## Scene list (all terminal footage is real recorded output)

| # | Visual | Source |
|---|--------|--------|
| 0 | Title card: "MintLens — know before you mint" | rendered card (bookend) |
| 1 | Live brief, Moth Club → verdict **Layak** | `cast/brief.cast` |
| 2 | Batch table: Moth Club **Layak** / Kitebots **Pantau** | `cast/batch.cast` |
| 3 | Agent process 1 researches; process 2 recalls from thread memory | `cast/memory.cast` |
| 4 | Findings card: 13 findings, the NO_PROXY bug fix (FINDINGS #12) | rendered card |
| 5 | End card: repo URL `github.com/Leira-ai/mintlens` | rendered card (bookend) |

Waiting time inside the live runs is compressed in editing (idle gaps in the
casts are capped); everything on screen is the actual output the terminal
produced, in the order it produced it.

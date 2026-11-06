# MintLens — demo video

Final video: **`mintlens-demo.mp4`** — 2 min 38 s, 1280×720, full English.
Built from **real asciinema recordings** of the product actually running in
a terminal — no simulated typing, no retyped output — with English voice
narration, styled subtitles, and an original instrumental music track
(`music_bgm.py`) mixed under the voice. Waiting time inside the live runs
is time-compressed in editing and labelled on screen
("LIVE RUN — waiting time compressed"); everything shown is the actual
output the terminal produced, in the order it produced it. The full
narration script and production notes are in
[DEMO-SCRIPT-v5.md](DEMO-SCRIPT-v5.md); the raw `.cast` recordings are
retained by the author as provenance for every scene.

| # | Segment | What it shows |
|---|---------|---------------|
| 1 | Hook / title | MintLens — know before you mint: a read-only BSC free-mint research agent on the OpenMinion SDK, Cortensor Hackathon #5 |
| 2 | Live CLI brief | `python mintlens.py brief 0x48c3…91c8 --fresh` recorded live — identity, Sourcify verification, dual-perspective free-path probe, market check; verdict **Layak** for Moth Club |
| 3 | Batch comparison | `python mintlens.py batch …` — Moth Club **Layak** vs Kitebots **Pantau** side by side, with the evidence for each verdict |
| 4 | Agent + memory | `memory_demo.py`: one process researches Moth Club; a second, separate process whose prompt contains no address recalls the contract and verdict from the shared `thread_id` (FINDINGS #10) |
| 5 | Findings close | 13 documented SDK findings, including the NO_PROXY bug (FINDINGS #12) and its fix with regression tests |
| 6 | End card | Read-only. Deterministic. Grounded. Repo: github.com/Leira-ai/mintlens |

## Production notes

- Terminal footage: asciinema `.cast` recordings of real 2026-11-06 runs
  (live brief, batch, memory demo), rendered through a terminal emulator;
  idle gaps capped in editing, output untouched — including genuine
  artefacts of the raw JSON output.
- Narration: English TTS voice-over following the script in
  DEMO-SCRIPT-v5.md, with styled subtitles throughout.
- Soundtrack: original composition by `music_bgm.py` (numpy synthesis),
  mixed low under the narration.
- This video (v5) replaces the earlier program-rendered walkthrough; the
  current file is the one to review.

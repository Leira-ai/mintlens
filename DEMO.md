# Demo

**▶ Watch the demo video: [`mintlens-demo.mp4`](mintlens-demo.mp4)**
(2 min 31 s, 1920×1080, English voice-over + subtitles — download the file
and play it locally; GitHub's web player may not preview an mp4 of this
size). The narration script, production notes, and an explicit scene
provenance live in [`DEMO-SCRIPT-v6.md`](DEMO-SCRIPT-v6.md).

> Prefer to run it yourself? The [README quickstart](README.md#quickstart--2-minutes)
> reproduces every workflow below in about two minutes.

## What the video shows

1. **The problem** — free mints on BNB Chain are a minefield; one
   innocent-looking claim can hide a honeypot or a drainer.
2. **A live, real brief** — `python mintlens.py brief 0x48c3…c0f0 --fresh`
   on Moth Club, recorded as it ran: Sourcify check, candidate free-mint
   functions probed, each simulated with zero value from a *fresh*
   address and from the *operator* wallet, market check — verdict
   **"Worth it"**, with the full reasons printed under it. The camera
   zooms to the verdict line as it appears and draws an animated
   highlight around it; that highlight is post-production, the text is
   the real output.
3. **Batch mode** — Moth Club and Kitebots researched in one run;
   the side-by-side summary table shows **Worth it** vs **Watch**
   (verified source, but no free path passed simulation).
4. **The conversational agent** (`agent.py`) — the SDK-memory workflow
   (one process researches, a second recalls it from the shared thread)
   is presented as an **explanatory card** in v6. Why: six live recording
   attempts on 2026-11-06 were all blocked by the OpenMinion runtime's
   freshness verifier ("Missing live-data evidence"), although the demo
   succeeded earlier the same day — its genuine transcript is in
   [`examples/memory-demo-transcript.txt`](examples/memory-demo-transcript.txt)
   and you can replay it any time with `python memory_demo.py`. Full
   disclosure in [`DEMO-SCRIPT-v6.md`](DEMO-SCRIPT-v6.md#scene-provenance--what-is-real-what-is-not).
   We chose an honest card over reusing older footage without saying so.
5. **The findings angle** — 13 SDK findings in
   [`FINDINGS.md`](FINDINGS.md), including #12 (bracketed IPv6 in
   `NO_PROXY` crashed every provider call — fix written, with regression
   tests) and #9 (`@tool` teach/confirm defaults gate read-only tools).

Motion design in v6: animated title/findings/end cards, smooth zoom
in/out and pans over the terminal footage, animated verdict highlights,
crossfade transitions, and a segment progress indicator. Waiting time
inside the recordings is time-compressed and labelled on screen
("LIVE RUN — waiting time compressed"); nothing else about the terminal
content is altered.

## Files

| File | What it is |
| --- | --- |
| `mintlens-demo.mp4` | The demo video (v6: 1080p, motion design, 2 min 31 s). |
| `DEMO-SCRIPT-v6.md` | Narration script + production notes + scene provenance for v6. |
| `DEMO-SCRIPT-v5.md` | The previous version's script/notes (720p static-card cut), kept for comparison. |
| `examples/memory-demo-transcript.txt` | Genuine terminal transcript of the cross-process memory demo (2026-11-06). |
| `demo-v6/render_v6.py` | The v6 video pipeline (asciinema replay + camera/highlight motion + card animation + captions) — kept locally with the project workspace, not tracked in git, same as the v5 pipeline. |

# Demo

**▶ Watch the demo video: [`mintlens-demo.mp4`](mintlens-demo.mp4)**
(2 min 31 s, 1920×1080, English voice-over + subtitles — download the file
and play it locally; GitHub's web player may not preview an mp4 of this
size). The narration script, production notes, and an explicit scene
provenance live in [`DEMO-SCRIPT-v7.md`](DEMO-SCRIPT-v7.md).

> Prefer to run it yourself? The [README quickstart](README.md#quickstart--2-minutes)
> reproduces every workflow below in about two minutes.

## What the video shows

1. **The problem** — free mints on BNB Chain are a minefield; one
   innocent-looking claim can hide a honeypot or a drainer.
2. **A live, real brief** — `python mintlens.py brief 0x48c3…c0f0 --fresh`
   on Moth Club, from the genuine live recording: Sourcify check,
   candidate free-mint functions probed, each simulated with zero value
   from a *fresh* address and from the *operator* wallet, market check —
   verdict **"Worth it"**, with the full reasons printed under it. The
   virtual camera pushes in to the verdict line as the highlight box
   draws itself around the real text; the highlight and camera are
   post-production, the text is the recorded output.
3. **Batch mode** — Moth Club and Kitebots researched in one run;
   the side-by-side summary table shows **Worth it** vs **Watch**
   (verified source, but no free path passed simulation), then both
   verdicts pop as cards.
4. **The conversational agent** (`agent.py`) — the SDK-memory workflow
   (one process researches, a second recalls it from the shared thread)
   is presented as an **explanatory card** in v7. Why: twelve live
   recording attempts on 2026-11-06 were all blocked by the OpenMinion
   runtime's freshness verifier ("Missing live-data evidence"), although
   the demo succeeded earlier the same day — its genuine transcript is in
   [`examples/memory-demo-transcript.txt`](examples/memory-demo-transcript.txt)
   and you can replay it any time with `python memory_demo.py`. Full
   disclosure in [`DEMO-SCRIPT-v7.md`](DEMO-SCRIPT-v7.md#scene-provenance--what-is-real-what-is-not).
   We chose an honest card over reusing older footage without saying so.
5. **The findings angle** — 13 SDK findings in
   [`FINDINGS.md`](FINDINGS.md), including #12 (bracketed IPv6 in
   `NO_PROXY` crashed every provider call — fix written, with regression
   tests) and #9 (`@tool` teach/confirm defaults gate read-only tools).

Motion design in v7: rebuilt in **Remotion** (React + TypeScript) after
v6's Pillow renderer was criticised — fairly — for stiff, linear motion.
Every entrance, camera move, and highlight is now driven by `spring()`
physics or bezier easing: letter-by-letter wordmark with overshoot,
word-by-word headline reveals, staggered status chips, a spring camera
push-in and eased pan over the terminal, self-drawing verdict
highlights, staggered findings cards from three directions, a spring
counter, varied scene transitions (slide / scale-through / rise /
drop-in — no plain crossfades), a five-layer stack (gradient mesh →
content → color grade → film grain → vignette), and a segment progress
indicator. Waiting time inside the recordings is time-compressed and
labelled on screen ("LIVE RUN — waiting time compressed"); nothing else
about the terminal content is altered.

## Files

| File | What it is |
| --- | --- |
| `mintlens-demo.mp4` | The demo video (v7: 1080p, Remotion motion design, 2 min 31 s). |
| `DEMO-SCRIPT-v7.md` | Narration script + production notes + scene provenance for v7. |
| `DEMO-SCRIPT-v6.md` | The previous version's script/notes (1080p Pillow-rendered cut), kept for comparison. |
| `DEMO-SCRIPT-v5.md` | The v5 script/notes (720p static-card cut), kept for comparison. |
| `examples/memory-demo-transcript.txt` | Genuine terminal transcript of the cross-process memory demo (2026-11-06). |
| `demo-v7/` | The v7 Remotion project (composition source + render script) — kept locally with the project workspace, not tracked in git, same as the v5/v6 pipelines. |

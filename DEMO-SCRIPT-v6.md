# MintLens — Demo Video Script & Production Notes (v6)

The narration script for `mintlens-demo.mp4` (v6), plus how the video was
made. **v6 is a full re-shoot at 1920×1080 with motion design** — animated
cards, camera moves on the terminal footage, verdict highlights — replacing
the 720p v5. One segment could not be re-recorded; see "Scene provenance"
below, which is deliberately explicit about it.

## Format

- **1920×1080, 30 fps, 2 min 31 s.** H.264 + AAC.
- English AI voice-over (TTS, same voice as v5), subtitles throughout,
  generated background music mixed under the voice.
- Structure: animated title → live CLI brief → live batch mode → agent
  memory (explanatory card — see provenance) → findings → animated end
  card. A progress bar + segment indicator ("02 / 06 LIVE BRIEF", dots)
  runs along the top.

## Narration script (as recorded)

**1 — Title / hook (0:01)**
> Free mints on BNB Chain are a minefield. Pools that promise a free mint
> can hide a honeypot or a wallet drainer behind one innocent-looking
> claim button. MintLens is a read-only research agent built on the
> OpenMinion SDK, created for Cortensor Hackathon number five. Give it a
> contract address, and before you risk a single transaction, it tells
> you whether the mint is worth it, worth only watching, or worth
> avoiding — and it shows its evidence.

**2 — Live brief, Moth Club (0:27)**
> This is a real run, recorded live. We ask MintLens for a brief on Moth
> Club, a collection it has never seen, with a fresh cache. It reads the
> contract's identity and checks whether the source is verified on
> Sourcify. Then it probes every plausible free-mint function and
> simulates each call with zero value, from two different perspectives: a
> fresh address, and the operator wallet — because a free quota that is
> already spent should not count as an open door. It also checks whether
> any market exists yet. The result: Worth it. A free path genuinely
> passed simulation, the source is verified, and every reason is listed
> under the verdict, so you can audit the call yourself.

**3 — Batch mode (1:12)**
> Point it at a whole list and it works down the list the same way,
> printing a comparison table at the end. Kitebots comes back Watch: its
> source is verified, but no free path passed simulation, so there is
> nothing safe to claim right now. Two contracts, two different calls,
> side by side, with the evidence for every verdict on one screen.

**4 — Agent memory (no narration — music only)**
> The memory segment is presented as an explanatory card in v6 (see
> "Scene provenance"). Intended narration, kept here for the next shoot:
> "The same engine also runs as a conversational agent, inside OpenMinion.
> Here it researches Moth Club in a first process. Then the process exits.
> A second, separate process is asked what it found — and answers from the
> shared thread alone: Moth Club, Worth it, free path found. That is SDK
> memory working across processes, not a script: session_id alone did not
> resume history; an explicit thread_id does."

**5 — Findings & close (1:56)**
> Building MintLens produced thirteen documented findings about the SDK,
> in the repo as FINDINGS.md. Two favourites: number twelve, a bracketed
> IPv6 entry in NO_PROXY crashed every provider call before a single
> request was sent. We wrote a fix for it, complete with regression
> tests. And number nine: read-only tools were gated behind interactive
> confirmation by default, so the defaults of the tool decorator really
> matter. MintLens never signs, never transacts, and never guesses. It
> checks the contract, so your wallet doesn't have to. The code, the
> findings, and a two-minute quickstart are all in the repository.

## Scene provenance — what is real, what is not

Everything terminal-shaped in v6 is a **real asciinema recording of the
current code**, replayed frame-for-frame by the renderer; nothing on
screen was retyped or edited. Only camera work (zoom/pan over the real
frames), an animated outline around the real verdict text, captions, and
cards were added in post.

| Scene | Source | Recorded |
| --- | --- | --- |
| CLI brief (Moth Club, `--fresh` → "Worth it") | `demo-v6/cast/brief.cast` | 2026-11-06, live |
| Batch (Moth Club "Worth it" vs Kitebots "Watch") | `demo-v6/cast/batch.cast` | 2026-11-06, live |
| Agent memory (two `agent.py` processes) | **not in v6** — explanatory card instead | see below |
| Title / findings / end cards | programmatic motion graphics (Pillow), no product footage | — |

**The memory scene, honestly.** The scene was attempted **six times** on
2026-11-06 (one initial recording + five retries spaced minutes apart,
per plan). Every attempt failed the same way: the OpenMinion runtime's
freshness verifier blocked the first agent process's answer
("Missing live-data evidence for a freshness-sensitive answer"), even
though the identical demo succeeded earlier the same day and its genuine
transcript ships in `examples/memory-demo-transcript.txt`. Rather than
fake the scene or silently reuse the v5 recording, v6 **omits the live
memory footage** and shows an honest card explaining the workflow and how
to replay it (`python memory_demo.py`). Re-shoot this segment when the
verifier cooperates; the narration for it is preserved above.

Also honest, as in v5: waiting time inside the recordings is compressed
(long provider/on-chain waits are capped), and the video says so on
screen ("LIVE RUN — waiting time compressed"). The compressed wait is
the only timeline change. The literal `\u2014` visible inside two JSON
reason strings is a genuine artefact of the program's own output,
kept as-is.

## How it was made

- Terminal scenes: `asciinema rec` (120×30) of the real commands with the
  MintLens cache deleted, replayed through a pyte screen buffer.
- Motion: the replay is rendered onto a supersampled virtual canvas
  (2880×1620) and a virtual camera adds a gentle push-in, a 1.5× zoom to
  the verdict line as it appears, a late pan across the reasons block,
  and animated rounded-box highlights (green = Worth it, amber = Watch)
  with a sweep-in and pulse. Cards use fade/slide/underline-sweep
  animation. Segments crossfade; a progress bar + dots track position.
- Voice: TTS (same voice family as v5). Music: `music_bgm.py`
  (procedural, generated for this video) under the voice.
- Pipeline: `demo-v6/render_v6.py` (extends the v5 renderer), casts and
  intermediates in `demo-v6/` (kept locally, not tracked in git — the
  brief/batch casts are the provenance for what you see).
- The v5 video, script, and pipeline remain in `demo-v5/` and
  `DEMO-SCRIPT-v5.md` for comparison.

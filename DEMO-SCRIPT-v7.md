# MintLens — Demo Video Script & Production Notes (v7)

The narration script for `mintlens-demo.mp4` (v7), plus how the video was
made. **v7 is a full rebuild of the motion layer in Remotion** (React +
TypeScript), replacing v6's frame-by-frame Pillow renderer. The criticism
of v6 was fair: almost every move was a linear interpolation, so the
animation felt stiff. In v7 every entrance, camera move, and highlight is
driven by `spring()` physics or bezier easing — there is no linear
interpolation on any decorative motion. The terminal content, narration,
music, and timeline are the same genuine material as v6, so the audio
could be reused unchanged.

## Format

- **1920×1080, 30 fps, 2 min 31 s.** H.264 + AAC.
- English AI voice-over (the v6 TTS takes, reused), subtitles throughout
  (same chunking algorithm as v6), the v6 generated background music
  mixed under the voice.
- Structure: animated title → live CLI brief → live batch mode → agent
  memory (explanatory card — see provenance) → findings → animated end
  card. A progress bar + segment indicator ("02 / 06 LIVE BRIEF", dots)
  runs along the top, as in v6.

## What actually moves differently in v7

Motion patterns follow the audited `claude-remotion-skill`
(github.com/haidrrrry/claude-remotion-skill, MIT — audited read-only
before adoption; audit notes live outside this repo):

1. **Title**: the wordmark enters letter-by-letter on a bouncy spring
   (stagger 3 frames/letter, overshoot), headlines reveal word-by-word
   on snappy springs, verdict pills pop with spring overshoot + a
   breathing glow, and background gradient blobs drift at three
   different parallax speeds.
2. **Scene transitions are all different**: scale-through (title),
   rise (brief), slide from right (batch), scale-through (memory),
   slide from left (findings), drop-in (end) — each with a faster eased
   exit. No plain crossfades.
3. **Terminal scenes**: the window itself springs in; the command types
   in with ease-out pacing; status chips pop in staggered; the JSON
   scrolls on an easeInOutQuint curve; the camera push-in to the verdict
   is a 1.45× move on the same quint curve with the focal point on the
   verdict line, followed by an eased pan across the reasons block; the
   highlight box **draws itself** around the real verdict text
   (scaleX spring) and pulses.
4. **Batch**: table rows slide in staggered, row tints draw themselves
   (scaleX), and the two verdict cards pop with bouncy springs, a
   slight rotation settle, and a breathing glow — green "Worth it",
   amber "Watch".
5. **Findings**: the "13" is an animated counter driven by a spring;
   the three finding cards enter staggered from three different
   directions (right / bottom / right).
6. **End card**: a 12-ray spark mark bursts in behind the wordmark with
   per-ray stagger, the repository URL underline draws itself, and the
   tagline reveals word-by-word.

Layer stack per the skill's rules: background mesh → scene content →
color grade → procedural film grain → vignette, on every frame.

## Narration script (as recorded — identical takes to v6)

**1 — Title / hook (0:01)**
> Free mints on BNB Chain are a minefield. Pools that promise a free mint
> can hide paid traps, fake quotas, and contracts that were never
> verified. MintLens checks a contract before you ever connect a wallet.
> It is a read-only research agent built on the OpenMinion SDK, created
> for Cortensor Hackathon number five. Give it a contract address, and
> it investigates, live and on-chain, then returns a verdict you can
> audit.

**2 — Live brief, Moth Club (0:27)**
> This is a real run, recorded live. MintLens reads the contract's
> identity straight from the chain. It checks the source code on
> Sourcify. Then it probes eight common free-mint methods, simulating
> every call with zero value, from two different perspectives: a fresh
> address, and the operator's own wallet. That distinction matters,
> because a path that is open to a new wallet may already be spent for
> yours. Finally, it checks whether any market exists. The verdict for
> Moth Club is Worth it. Verified source code, and a free mint path that
> passes simulation.

**3 — Batch mode (1:12)**
> MintLens can also say no. In batch mode, it compares contracts side by
> side, with the evidence for every verdict on one line. Kitebots is
> verified too, but no free path passed simulation, so its verdict is
> Watch. Same checks, same honesty, whether the answer is yes or no.

**4 — Agent memory (no narration — music only)**
> The memory segment is presented as an explanatory card in v7 (see
> "Scene provenance"). Intended narration, kept here for the next shoot:
> "The same engine also runs as a conversational agent, inside
> OpenMinion. Here it researches Moth Club in a first process. Then the
> process exits. A second, separate process is asked what it found — and
> answers from the shared thread alone: Moth Club, Worth it, free path
> found. That is SDK memory working across processes, not a script:
> session_id alone did not resume history; an explicit thread_id does."

**5 — Findings & close (1:56)**
> Building MintLens surfaced thirteen documented findings about the
> OpenMinion SDK: what worked, what surprised us, and what broke. One
> finding was a real bug, a common proxy setting that crashed every
> provider call. We wrote a fix for it, complete with regression tests.
> MintLens never signs, never transacts, and never guesses. It just does
> the homework, before your wallet is on the line. The code is public.
> Thank you for watching.

## Scene provenance — what is real, what is not

The terminal text in v7 is **the exact output text of the genuine v6
asciinema recordings** (`demo-v6/cast/brief.cast`, `batch.cast` — real
runs of the current code on 2026-11-06), extracted programmatically from
the cast files and hard-wrapped at 116 columns the way the 120-column
terminal wrapped it. Nothing was retyped, edited, or mocked up; the
literal `\u2014` inside two JSON reason strings is a genuine artefact of
the program's own output, kept as-is (also noted in v6). What changed vs
v6 is only the presentation layer: instead of replaying the VT stream,
Remotion types/scrolls the recorded text and moves a virtual camera over
it. Waiting time inside the recordings is compressed, and the video
says so on screen ("LIVE RUN — waiting time compressed").

| Scene | Source | Notes |
| --- | --- | --- |
| CLI brief (Moth Club, `--fresh` → "Worth it") | text of `demo-v6/cast/brief.cast` | recorded live 2026-11-06 |
| Batch (Moth Club "Worth it" vs Kitebots "Watch") | text of `demo-v6/cast/batch.cast` (summary table) | recorded live 2026-11-06; the full JSON briefs the real run prints are noted on screen, not shown |
| Agent memory (two `agent.py` processes) | **not in v7** — explanatory card instead | see below |
| Title / findings / end cards | Remotion motion graphics, no product footage | — |
| Voice / music / subtitles | v6 audio takes + v6 chunking algorithm | same takes, same timeline; one mastering step: Remotion rendered the mix ≈7 dB quieter than v6, so the finished file's audio was gained +5 dB (peak −4.5 dB, no clipping) to match v6 loudness |

**The memory scene, honestly.** On 2026-11-06 the scene was attempted
**twelve times in total**: six asciinema recordings for v6 (one initial +
five retries), four further manual attempts that afternoon, and two more
recordings for v7 in the evening. Every attempt failed the same way: the
OpenMinion runtime's freshness verifier blocked the first agent
process's answer ("Missing live-data evidence for a freshness-sensitive
answer"), even though the identical demo succeeded earlier the same day
and its genuine transcript ships in
`examples/memory-demo-transcript.txt`. Rather than fake the scene or
silently reuse stale footage, v7, like v6, **omits the live memory
footage** and shows an honest card explaining the workflow and how to
replay it (`python memory_demo.py`). Re-shoot this segment when the
verifier cooperates; the narration for it is preserved above.

## How it was made

- Composition: Remotion 4 (React 19 + TypeScript) in
  `cortensor-hackathon-5/remotion-v7/` (project workspace, not tracked in
  this repo — same convention as the v5/v6 pipelines). One composition,
  six `<Sequence>` scenes, a single theme object (colors, bezier
  easings, spring presets).
- Motion rules (from the audited skill): no linear interpolation on
  decorative motion; entrances animate 2–3 properties together; 3–6
  frame staggers; exits faster than entrances; five-layer stack
  (mesh → assets → graphics → grade → grain + vignette); idle elements
  breathe (sin-wave micro-motion on glows, dots, and drift chips).
- Verification loop (mandatory in the skill, and in this project):
  stills were rendered and visually inspected at the title, mid-brief,
  verdict zoom, batch, memory, findings, and end frames **before** the
  full render; two defects found that way (camera focal point cutting
  the verdict line; unwrapped JSON lines overflowing the window) were
  fixed and the stills re-checked. The finished mp4 was then verified
  with ffprobe and frame extraction at ±5 s, 30 s, 60 s, 90 s, 120 s,
  and the final seconds.
- Render environment note: Remotion's bundled Chromium download stalled
  in this sandbox, so a Chrome Headless Shell 123 binary was fetched
  directly and passed via `--browser-executable`; Remotion's
  port-availability probe also had to be patched locally (loopback only)
  because the sandbox's transparent proxy makes every 0.0.0.0 port look
  occupied. Both are local tooling workarounds in `node_modules`/project
  scratch, not changes to the video or the product.
- Fonts: DejaVu Sans / DejaVu Sans Mono (system fonts in the render
  environment) — a deliberate offline-safe choice; no webfont downloads.
- The v6 video, script, and pipeline remain in `demo-v6/` and
  `DEMO-SCRIPT-v6.md` for comparison; v5 likewise.

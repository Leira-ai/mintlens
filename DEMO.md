# MintLens — demo video

Final video: **`mintlens-demo.mp4`** — 73 seconds, full English, a product
walkthrough (how to access it → how to use it → what the result means) with
styled subtitles and an instrumental music track. All terminal excerpts are
from real runs on 2026-11-06, excerpted for length; nothing is mocked up.

| # | Segment | What it shows |
|---|---------|---------------|
| 1 | Title | MintLens — a read-only BSC free-mint research agent, built on the OpenMinion SDK · Cortensor Hackathon #5 |
| 2 | Getting set up | Provider configuration: how the agent gets a real model (echo for plumbing → Gemini via Google's OpenAI-compatible endpoint) |
| 3 | Usage — CLI brief | `python mintlens.py brief 0x8b8e…1db0` — five deterministic checks, no model; verdict Pantau for Kitebots |
| 4 | Usage — AI agent | `python agent.py "Research this BSC contract: …"` — the agent calls its own research tool and answers from the tool output; verdict matches the CLI |
| 5 | The result | How to read the verdict: Layak (worth it) / Pantau (monitor) / Hindari (avoid), and why an Agent-ID-gated path is reported "not detected", never "does not exist" |
| 6 | The agent remembers | A new process with the same explicit `thread_id` recalls the earlier contract and verdict (finding #10) |
| 7 | Behind the scenes | Building blocks used (Agent facade, `@tool` policy annotations, providers, thread sessions, `observed_at` evidence); signing and SSH modules deliberately NOT enabled |
| 8 | Close | Read-only. Deterministic. Grounded. Full code + README + findings in this repo |

## Production notes

- Rendered by `render_demo2.py` (Pillow + ffmpeg): typed terminal animation
  from the real run outputs, styled subtitle bar, fade transitions between
  segments.
- Soundtrack composed by `music_bgm.py` (numpy synthesis, Karplus-Strong
  plucked melody in A-minor pentatonic over an Am–F–C–G progression at
  100 BPM, with bass, pads and soft offbeat hats). Measured loudness:
  −16.0 dB mean / −0.4 dB peak — clearly audible under the visuals.
  (Earlier drafts used a sine-pad drone that measured −39.9 dB at v2 and
  −27.3 dB at v3; the composed track replaced it.)
- Re-render: `python render_demo2.py mintlens-demo.mp4` from the project
  venv (system `python3` is used for the BGM step, which needs numpy).

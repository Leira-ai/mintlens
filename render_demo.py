"""Render the MintLens demo video (captioned slides) with Pillow + ffmpeg.

All terminal excerpts are from real runs on 2026-11-06 (Kitebots brief,
model-backed agent run, and the cross-process thread-recall run).
Usage: python render_demo.py [output.mp4]
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
BG = (13, 17, 23)
FG = (230, 237, 243)
DIM = (139, 148, 158)
ACCENT = (88, 166, 255)
GREEN = (63, 185, 80)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
f_title = ImageFont.truetype(FONTB, 34)
f_h = ImageFont.truetype(FONTB, 26)
f_body = ImageFont.truetype(FONT, 21)
f_small = ImageFont.truetype(FONT, 17)

SLIDES: list[tuple[str, list[tuple[str, str]], int]] = [
    (
        "MintLens",
        [
            ("A read-only research agent for BSC free-mint opportunities.", "fg"),
            ("", "fg"),
            ("Built on the OpenMinion SDK", "accent"),
            ("Cortensor Hackathon #5", "dim"),
        ],
        6,
    ),
    (
        "The problem",
        [
            ("Free mints in the Agent-ID ecosystem appear fast,", "fg"),
            ("and most are unclear projects.", "fg"),
            ("", "fg"),
            ("Checking one contract by hand means verifying its", "fg"),
            ("identity, its source code, whether a free path is", "fg"),
            ("still open, and whether any market exists.", "fg"),
            ("", "fg"),
            ("MintLens automates that first-pass verification.", "accent"),
        ],
        7,
    ),
    (
        "How it works — 5 deterministic checks",
        [
            ("1. Identity        eth_call: name / symbol / supply / owner", "fg"),
            ("2. Verification    Sourcify v2 match + contract name", "fg"),
            ("3. Free-path probe value-0 simulation of 8 mint/claim", "fg"),
            ("                   methods, from TWO sender perspectives", "fg"),
            ("4. Market          DexScreener: best BSC pair + liquidity", "fg"),
            ("5. Verdict         Layak / Pantau / Hindari (fixed rules)", "fg"),
            ("", "fg"),
            ("The LLM only orchestrates tools and narrates.", "accent"),
            ("It never decides the verdict and never signs anything.", "accent"),
        ],
        9,
    ),
    (
        "Terminal 1 — deterministic brief (no model)",
        [
            ("$ python mintlens.py brief 0x8b8e59c0...1db0", "green"),
            ("{", "dim"),
            ('  "contract": {"name": "Kitebots", "symbol": "KITE",', "fg"),
            ('               "totalSupply": 668, ...},', "fg"),
            ('  "verification": {"verified": true,', "fg"),
            ('                   "match": "exact_match"},', "fg"),
            ('  "free_paths": {"has_free_path_signal": false, ...},', "fg"),
            ('  "market": {"has_market": false},', "fg"),
            ('  "verdict": "Pantau"', "accent"),
            ("}", "dim"),
        ],
        10,
    ),
    (
        "Terminal 2 — agent run, real model (Gemini)",
        [
            ('$ python agent.py "Research this BSC contract:', "green"),
            ('                   0x8b8e59c0...1db0"', "green"),
            ("", "fg"),
            ("openminion: Research results for 0x8b8e...1db0:", "fg"),
            (" * Identity: Kitebots (KITE), supply 668", "fg"),
            (" * Sourcify: verified (exact match)", "fg"),
            (" * Free-mint path: not detected from a plain", "fg"),
            ("   address — the gate may be identity-based", "fg"),
            (" * Market: no BSC pair on DexScreener", "fg"),
            (" * Verdict: Pantau", "accent"),
            ("(actual output, excerpted; matches the CLI brief)", "dim"),
        ],
        12,
    ),
    (
        "Terminal 3 — thread memory across processes",
        [
            ('$ python agent.py "Which contract did I ask you', "green"),
            ('   to research before, and what was the verdict?"', "green"),
            ("", "fg"),
            ("openminion: You asked about 0x8b8e59c0...1db0.", "fg"),
            ('The verdict was "Pantau", because:', "fg"),
            (" * no free mint/claim path passed simulation,", "fg"),
            (" * no DEX pair exists yet,", "fg"),
            (" * although the contract is Sourcify-verified,", "fg"),
            ("   mint access may be identity-gated.", "fg"),
            ("", "fg"),
            ("Continuity key: explicit thread_id on Agent.run().", "accent"),
        ],
        11,
    ),
    (
        "The key idea — who asks matters",
        [
            ("A value-0 simulation is a statement about", "fg"),
            ("(contract, sender, block) — not the contract alone.", "fg"),
            ("", "fg"),
            ("fresh address passes + operator fails", "fg"),
            ("   -> free path exists, operator quota spent", "dim"),
            ("everyone fails + contract verified", "fg"),
            ("   -> possibly identity-gated: report", "dim"),
            ('      "not detected", never "does not exist"', "dim"),
            ("", "fg"),
            ("One probe conflates these; two separate them.", "accent"),
        ],
        9,
    ),
    (
        "OpenMinion building blocks used",
        [
            ("* Agent facade + @tool (3 read-only tools)", "fg"),
            ('* Tool policy annotations: min_scope="READ_ONLY"', "fg"),
            ("* Pluggable providers: echo -> Gemini via the", "fg"),
            ("  official OpenAI-compatible endpoint", "fg"),
            ("* Sessions: explicit thread_id resumes history", "fg"),
            ("* Freshness verification: observed_at evidence", "fg"),
            ("* Runtime config: providers, timeouts, state", "fg"),
            ("", "fg"),
            ("Not enabled, by design: signing + SSH tool modules.", "accent"),
        ],
        9,
    ),
    (
        "Findings for the OpenMinion team (12)",
        [
            ("#7  No native Gemini provider in 0.1.18", "fg"),
            ("#8  Model availability is per-account (404/503)", "fg"),
            ("#9  Bare @tool defaults gate read-only tools", "fg"),
            ("    behind interactive confirmation", "dim"),
            ("#10 session_id alone does not resume history;", "fg"),
            ("    thread_id does", "dim"),
            ("#11 Freshness verifier needs dated evidence", "fg"),
            ("    keys inside tool outputs", "dim"),
            ("#12 Malformed NO_PROXY env crashes httpx with", "fg"),
            ("    a misleading provider error", "dim"),
            ("", "fg"),
            ("Full notes: FINDINGS.md in the repo.", "accent"),
        ],
        9,
    ),
    (
        "MintLens",
        [
            ("Read-only by construction.", "fg"),
            ("Deterministic verdicts. Grounded narration.", "fg"),
            ("No keys, no signing, no transactions.", "fg"),
            ("", "fg"),
            ("Code, README and full findings in the repo.", "accent"),
            ("Thank you.", "dim"),
        ],
        6,
    ),
]

COLORS = {"fg": FG, "dim": DIM, "accent": ACCENT, "green": GREEN}


def render_slide(idx: int, title: str, lines: list[tuple[str, str]]) -> Path:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 64], fill=(22, 27, 34))
    d.text((40, 16), f"MintLens demo — {idx + 1}/{len(SLIDES)}", font=f_small, fill=DIM)
    y = 110
    d.text((60, y), title, font=f_title, fill=FG)
    y += 70
    for text, color in lines:
        for chunk in textwrap.wrap(text, width=76) or [""]:
            d.text((60, y), chunk, font=f_body, fill=COLORS[color])
            y += 32
        if text == "":
            y += 6
    out = Path(f"/tmp/mintlens-slides/slide_{idx:02d}.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("mintlens-demo.mp4")
    frames = []
    concat_lines: list[str] = []
    for i, (title, lines, dur) in enumerate(SLIDES):
        p = render_slide(i, title, lines)
        frames.append(p)
        concat_lines.append(f"file '{p}'")
        concat_lines.append(f"duration {dur}")
    concat_lines.append(f"file '{frames[-1]}'")
    listfile = Path("/tmp/mintlens-slides/list.txt")
    listfile.write_text("\n".join(concat_lines) + "\n")
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
            "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "medium",
            str(output),
        ],
        check=True,
        capture_output=True,
    )
    total = sum(d for _, _, d in SLIDES)
    print(f"wrote {output} ({output.stat().st_size} bytes, ~{total}s of slides)")


if __name__ == "__main__":
    main()

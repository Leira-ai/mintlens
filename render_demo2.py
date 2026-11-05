"""MintLens demo v2 — product walkthrough ("sneak peek") video.

Structure: how to access it -> how to use it (CLI + agent) -> the results ->
thread memory -> behind the scenes -> close. Terminal scenes type the real
commands and reveal the real outputs of the 2026-11-06 runs line by line.
Styled subtitles (Indonesian), fade transitions between segments, and a
synthesized pad BGM underneath.

Usage: python render_demo2.py [output.mp4]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 10
BG = (10, 13, 18)
PANEL = (17, 22, 30)
HEADER = (24, 31, 42)
FG = (230, 237, 243)
DIM = (148, 158, 170)
ACCENT = (88, 166, 255)
GREEN = (63, 185, 80)
AMBER = (210, 168, 60)
RED = (224, 108, 108)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
f_big = ImageFont.truetype(FONTB, 54)
f_title = ImageFont.truetype(FONTB, 30)
f_body = ImageFont.truetype(FONT, 21)
f_bodyb = ImageFont.truetype(FONTB, 21)
f_term = ImageFont.truetype(FONT, 20)
f_sub = ImageFont.truetype(FONTB, 22)

WORK = Path("/tmp/ml2")
ADDR = "0x8b8e59c014eb3e229e043ae8f3b0d7e201d21db0"
ADDR_SHORT = "0x8b8e59c0...1db0"


def base_frame(seg_title: str, subtitle: str) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    # header chip
    d.ellipse([36, 26, 48, 38], fill=ACCENT)
    d.text((58, 18), seg_title, font=f_title, fill=FG)
    d.line([0, 62, W, 62], fill=(40, 48, 60), width=2)
    if subtitle:
        # styled subtitle bar: translucent black, accent strip, bold text
        lines = []
        words, cur = subtitle.split(), ""
        for w_ in words:
            if len(cur) + len(w_) + 1 > 62:
                lines.append(cur)
                cur = w_
            else:
                cur = (cur + " " + w_).strip()
        if cur:
            lines.append(cur)
        bar_h = 34 * len(lines) + 22
        y0 = H - 26 - bar_h
        d.rounded_rectangle([70, y0, W - 70, H - 26], radius=12, fill=(0, 0, 0, 178))
        d.rounded_rectangle([70, y0, 78, H - 26], radius=4, fill=ACCENT + (255,))
        ty = y0 + 12
        for ln in lines:
            tw = d.textlength(ln, font=f_sub)
            d.text(((W - tw) / 2, ty), ln, font=f_sub, fill=(255, 255, 255))
            ty += 34
    return img


def draw_terminal(img: Image.Image, lines: list[tuple[str, tuple]]) -> None:
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([60, 92, W - 60, 596], radius=14, fill=PANEL)
    d.rounded_rectangle([60, 92, W - 60, 136], radius=14, fill=HEADER)
    d.rectangle([60, 122, W - 60, 136], fill=HEADER)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([84 + i * 30, 105, 100 + i * 30, 121], fill=c)
    d.text((190, 103), "mintlens — bash", font=f_term, fill=DIM)
    visible = lines[-13:]
    y = 156
    for text, color in visible:
        d.text((88, y), text, font=f_term, fill=color)
        y += 33


def card_lines(img: Image.Image, items: list[tuple[str, tuple, object]], reveal: int) -> None:
    d = ImageDraw.Draw(img)
    y = 150
    for i, (text, color, font) in enumerate(items):
        if i < reveal:
            d.text((90, y), text, font=font, fill=color)
        y += 46 if font is f_body else 64


def save_frames(seg_idx: int, frames: list[Image.Image]) -> float:
    folder = WORK / f"seg{seg_idx}"
    folder.mkdir(parents=True, exist_ok=True)
    for i, fr in enumerate(frames):
        fr.save(folder / f"f{i:04d}.png")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i",
         str(folder / "f%04d.png"), "-vf", "fps=30,format=yuv420p,settb=AVTB",
         "-c:v", "libx264", "-preset", "medium", str(WORK / f"seg{seg_idx}.mp4")],
        check=True,
    )
    return len(frames) / FPS


def card_segment(idx, title, subtitle, items, seconds):
    frames = []
    total = int(seconds * FPS)
    for t in range(total):
        img = base_frame(title, subtitle)
        reveal = min(len(items), 1 + t // 3)
        card_lines(img, items, reveal)
        frames.append(img)
    return save_frames(idx, frames)


def term_segment(idx, title, subtitles, script, out_hold=3):
    """script: list of (kind, payload). subtitles: [(until_event_idx, text)]"""
    # Expand script into per-frame line states.
    states: list[tuple[list, str]] = []
    lines: list[tuple[str, tuple]] = []
    sub_text = subtitles[0][1] if subtitles else ""
    event_no = 0

    def current_sub():
        s = subtitles[0][1] if subtitles else ""
        for until, txt in subtitles:
            if event_no >= until:
                s = txt
        return s

    def push(n=1):
        for _ in range(n):
            states.append((list(lines), current_sub()))

    for kind, payload in script:
        if kind == "cmd":
            text = payload
            for n in range(1, len(text) + 1, 2):
                states.append((list(lines) + [("$ " + text[:n], GREEN)], current_sub()))
            lines.append(("$ " + text, GREEN))
            push(4)
        elif kind == "out":
            text, color = payload
            lines.append((text, color))
            push(out_hold)
        elif kind == "wait":
            push(int(payload * FPS))
        event_no += 1
    push(10)
    frames = []
    for snap_lines, sub in states:
        img = base_frame(title, sub)
        draw_terminal(img, snap_lines)
        frames.append(img)
    return save_frames(idx, frames)


def build() -> list[float]:
    WORK.mkdir(parents=True, exist_ok=True)
    durs = []

    # 1 — intro card
    durs.append(card_segment(0, "MintLens — sneak peek", "",
        [("MintLens", ACCENT, f_big),
         ("Agen riset mint gratis BSC — hanya membaca data.", FG, f_body),
         ("", FG, f_body),
         ("Di video ini: cara akses -> cara pakai -> hasilnya.", FG, f_body),
         ("Dibangun di atas OpenMinion SDK · Cortensor Hackathon #5", DIM, f_body)], 7))

    # 2 — access / setup (terminal)
    durs.append(term_segment(1, "1 · Cara akses — setup provider",
        [(0, "Aksesnya cukup konfigurasi: provider model diatur di .openminion/agents.json"),
         (4, "API key disimpan di luar repo, lewat environment — tidak pernah ter-commit")],
        [("cmd", "cd mintlens && ls"),
         ("out", ("agent.py   mintlens.py   README.md   FINDINGS.md", FG)),
         ("cmd", "openminion --version"),
         ("out", ("0.1.18", FG)),
         ("wait", 0.8),
         ("cmd", "grep -E 'provider|model' .openminion/agents.json"),
         ("out", ('"provider": "openai"  -> endpoint resmi Gemini', FG)),
         ("out", ('"model": "gemini-3.1-flash-lite"', FG)),
         ("out", ('"api_key_env": "OPENAI_API_KEY"', DIM)),
         ("wait", 1.2),
         ("cmd", "export OPENAI_API_KEY=**********"),
         ("out", ("siap. dua cara pakai: CLI deterministik, atau agen AI.", ACCENT))]))

    # 3 — CLI brief (terminal)
    durs.append(term_segment(2, "2 · Cara pakai — brief CLI (tanpa model)",
        [(0, "Mode CLI: lima cek deterministik, tanpa AI — hasilnya selalu sama"),
         (6, "Verdict dari aturan kode: Layak, Pantau, atau Hindari")],
        [("cmd", f"python mintlens.py brief {ADDR}"),
         ("out", ("{ brief untuk 0x8b8e59c0...1db0", DIM)),
         ("out", ("  contract    : Kitebots (KITE), supply 668", FG)),
         ("out", ("                  owner 0x4e9b...08dba", FG)),
         ("out", ("  verification: Sourcify exact_match", FG)),
         ("out", ("  free_paths  : 8 metode x 2 sudut pandang", FG)),
         ("out", ("     freeMint()   fresh=revert  operator=revert", DIM)),
         ("out", ("     claimFree()  fresh=revert  operator=revert", DIM)),
         ("out", ("  market      : tidak ada pair DEX", FG)),
         ("out", ('  verdict     : "Pantau" }', ACCENT)),
         ("wait", 1.5)]))

    # 4 — agent run (terminal)
    durs.append(term_segment(3, "3 · Cara pakai — agen AI (model beneran)",
        [(0, "Mode agen: AI memanggil tool risetnya sendiri, lalu merangkum"),
         (4, "Hasil agen sama dengan brief CLI — verdict Pantau, tanpa karangan")],
        [("cmd", f'python agent.py "Research this BSC contract: {ADDR_SHORT}"'),
         ("wait", 0.6),
         ("out", ("openminion: Hasil riset untuk 0x8b8e...1db0:", FG)),
         ("out", (" * Identity : Kitebots (KITE), supply 668", FG)),
         ("out", (" * Sourcify : Terverifikasi (Exact Match)", FG)),
         ("out", (" * Jalur gratis: tidak terdeteksi — semua", FG)),
         ("out", ("   simulasi value-0 revert dari alamat uji", FG)),
         ("out", (" * Market   : belum ada pair DEX di BSC", FG)),
         ("out", (" * Verdict  : Pantau", ACCENT)),
         ("wait", 1.5),
         ("out", ("(output asli run 6 Nov 2026, dipersingkat)", DIM))], out_hold=4))

    # 5 — verdict card
    durs.append(card_segment(4, "4 · Hasilnya — cara membaca verdict",
        "Pantau = ada sinyal positif (kode terverifikasi), tapi jalur gratis belum terbukti terbuka",
        [("Layak    jalur gratis lolos simulasi + kode terverifikasi", GREEN, f_body),
         ("Pantau   ada sinyal positif, bukti belum lengkap", AMBER, f_bodyb),
         ("Hindari  tidak ada sinyal positif / bukan kontrak", RED, f_body),
         ("", FG, f_body),
         ("Kitebots -> Pantau.", FG, f_body),
         ("Kemungkinan ter-gate Agent ID: dari alamat biasa", DIM, f_body),
         ('selalu revert — dilaporkan "tidak terdeteksi",', DIM, f_body),
         ('bukan "tidak ada".', DIM, f_body)], 12))

    # 6 — thread memory (terminal)
    durs.append(term_segment(5, "5 · Sesi agen mengingat",
        [(0, "Proses baru, sesi yang sama: agen mengingat penelitian sebelumnya"),
         (3, "Kuncinya thread_id eksplisit — session_id saja tidak cukup (temuan #10)")],
        [("cmd", 'python agent.py "Which contract did I ask you to'),
         ("out", ('   research before, and what was the verdict?"', GREEN)),
         ("wait", 0.6),
         ("out", ("openminion: Anda meminta saya meneliti", FG)),
         ("out", ("0x8b8e59c0...1db0. Verdict-nya: Pantau.", FG)),
         ("out", ("Alasannya: tidak ada jalur mint/claim gratis", FG)),
         ("out", ("yang lolos simulasi, belum ada pair DEX, dan", FG)),
         ("out", ("akses mint mungkin dibatasi syarat khusus", FG)),
         ("out", ("meski kontrak terverifikasi di Sourcify.", FG)),
         ("wait", 1.5),
         ("out", ("(output asli run 6 Nov 2026, dipersingkat)", DIM))], out_hold=4))

    # 7 — behind the scenes card
    durs.append(card_segment(6, "6 · Di balik layar",
        "12 temuan SDK dicatat di FINDINGS.md — bahan kriteria Building Blocks (25%)",
        [("Building blocks OpenMinion yang dipakai:", FG, f_bodyb),
         (" * Agent facade + @tool (3 tool hanya-baca)", FG, f_body),
         (' * Policy: min_scope="READ_ONLY", idempotent', FG, f_body),
         (" * Provider pluggable (echo -> Gemini)", FG, f_body),
         (" * Sesi thread + bukti bertanggal observed_at", FG, f_body),
         ("", FG, f_body),
         ("Sengaja TIDAK diaktifkan: modul tanda tangan", DIM, f_body),
         ("blockchain dan SSH. MintLens murni membaca.", DIM, f_body)], 12))

    # 8 — closing card
    durs.append(card_segment(7, "MintLens",
        "Riset dulu, mutusin kemudian.",
        [("MintLens", ACCENT, f_big),
         ("Read-only. Deterministic. Grounded.", FG, f_body),
         ("Tidak ada kunci, tidak ada tanda tangan,", FG, f_body),
         ("tidak ada transaksi.", FG, f_body),
         ("", FG, f_body),
         ("Kode + README + temuan lengkap: repo MintLens", DIM, f_body),
         ("Cortensor Hackathon #5 — terima kasih.", DIM, f_body)], 7))
    return durs


CHORDS = [  # Am, F, C, G — soft pad, 4 s each
    (110.00, 130.81, 164.81),
    (87.31, 110.00, 130.81),
    (130.81, 164.81, 196.00),
    (98.00, 123.47, 146.83),
]


def make_bgm(total_s: float) -> Path:
    chord_files = []
    for i, freqs in enumerate(CHORDS):
        cf = WORK / f"chord{i}.wav"
        inputs, mix = [], []
        for j, fq in enumerate(freqs):
            inputs += ["-f", "lavfi", "-i", f"sine=frequency={fq}:duration=4.2"]
            mix.append(f"[{j}:a]")
        fc = ("".join(mix) + "amix=inputs=3:normalize=0,"
              "afade=t=in:st=0:d=0.9,afade=t=out:st=3.3:d=0.9,lowpass=f=750,volume=0.5[a]")
        subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc,
                        "-map", "[a]", str(cf)], check=True)
        chord_files.append(cf)
    concat = WORK / "chords.txt"
    concat.write_text("".join(f"file '{c}'\n" for c in chord_files))
    bgm = WORK / "bgm.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-t", f"{total_s:.2f}", "-af",
         f"volume=0.16,afade=t=in:st=0:d=2,afade=t=out:st={total_s - 3:.2f}:d=3",
         str(bgm)], check=True)
    return bgm


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("mintlens-demo-v2.mp4")
    durs = build()
    print("segment durations:", [round(d, 1) for d in durs])
    fade = 0.6
    # xfade chain
    inputs = []
    for i in range(len(durs)):
        inputs += ["-i", str(WORK / f"seg{i}.mp4")]
    filters, last, total = [], "0:v", durs[0]
    for i in range(1, len(durs)):
        out_label = f"v{i}"
        offset = total - fade
        filters.append(f"[{last}][{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.2f}[{out_label}]")
        last = out_label
        total += durs[i] - fade
    video_only = WORK / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex",
                    ";".join(filters), "-map", f"[{last}]", "-c:v", "libx264",
                    "-preset", "medium", "-pix_fmt", "yuv420p", str(video_only)], check=True)
    bgm = make_bgm(total)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(video_only), "-i", str(bgm),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "96k", "-shortest", str(output)], check=True)
    print(f"wrote {output} ({output.stat().st_size} bytes, ~{total:.0f}s)")


if __name__ == "__main__":
    main()

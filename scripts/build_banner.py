#!/usr/bin/env python3
"""Generate assets/banner.svg, the animated README banner.

Pure CSS-animated SVG (no JS) so it autoplays inside a GitHub README.
Every animation shares one 10s clock; times below are in seconds.

    python3 scripts/build_banner.py

See docs/banner-spec.md for the creative brief and scene breakdown.
"""

import base64
import html
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "banner.svg"
FONTS = Path(__file__).resolve().parent / "fonts"

W, H = 1280, 400
CX, CY = W / 2, H / 2
LOOP = 10.0

# palette: apple light, icy blue accent
BG = "#fbfbfd"
INK = "#1d1d1f"
GRAY = "#86868b"
BORDER = "#e5e5ea"
ICE = "#9ad8ff"
ICE_INK = "#3a9be6"  # ice blue dark enough to read on white

# fast in, soft landing
EXPO_OUT = "cubic-bezier(.16,1,.3,1)"
EASE_IN = "cubic-bezier(.6,0,.9,.4)"
LINEAR = "linear"
STEP = "step-end"

# scene copy
NAME = "ayaan faisal"
SUBTITLE = "welcome to my github"
ALWAYS = "always"
ROLL_WORDS = ["building.", "experimenting.", "vibecoding."]
HERO = ["you", "can", "just", "build", "things."]
HERO_ACCENT = "build"
STATUS = [
    "student @ uwaterloo",
    "interning @ tribalscale",
    "seeking summer 2027 internships",
]
SCRAMBLE_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789#%*/_-+=!?$"

css_rules = []
_counter = 0


def pct(t):
    return f"{t / LOOP * 100:.3f}%"


def anim(frames, extra=""):
    """Register a keyframe animation and return a class name for it.

    frames: list of (time_s, css_props, easing_into_next_frame).
    Frames are padded so the value holds steady to 0% and 100%.
    """
    global _counter
    _counter += 1
    name = f"a{_counter}"
    first, last = frames[0], frames[-1]
    if first[0] > 0:
        frames = [(0, first[1], STEP)] + frames
    if last[0] < LOOP:
        frames = frames + [(LOOP, last[1], LINEAR)]
    body = "".join(
        f"{pct(t)}{{{props};animation-timing-function:{ease}}}"
        for t, props, ease in frames
    )
    css_rules.append(f"@keyframes {name}{{{body}}}")
    css_rules.append(f".{name}{{animation:{name} {LOOP}s infinite;{extra}}}")
    return name


def tf(scale=1.0, dx=0, dy=0, op=None):
    s = f"transform:translate({dx}px,{dy}px) scale({scale})"
    if op is not None:
        s += f";opacity:{op}"
    return s


def origin(y=CY):
    return f"transform-box:view-box;transform-origin:{CX}px {y}px"


def window(start, end):
    """Hard on/off visibility between start and end (for decode frames)."""
    return anim([(0, "opacity:0", STEP), (start, "opacity:1", STEP), (end, "opacity:0", STEP)])


def rise(t_in, t_out, dist, y, settle=0.45):
    """Mask reveal: slide up into a clipped slot, hold, slide up and out."""
    return anim(
        [
            (t_in, tf(1.04, dy=dist), EXPO_OUT),
            (t_in + settle, tf(1), LINEAR),
            (t_out - 0.28, tf(1), EASE_IN),
            (t_out, tf(0.98, dy=-dist), STEP),
        ],
        origin(y),
    )


def slot(y_top, y_bottom, inner):
    """Static clip window that a rising line is revealed through."""
    global _counter
    _counter += 1
    cid = f"s{_counter}"
    return (
        f'<clipPath id="{cid}"><rect x="0" y="{y_top}" width="{W}" height="{y_bottom - y_top}"/></clipPath>'
        f'<g clip-path="url(#{cid})">{inner}</g>'
    )


def font_face(family, file, weight):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return (
        f"@font-face{{font-family:'{family}';font-weight:{weight};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    )


# ---------------------------------------------------------------- background

def glow():
    """Faint ice light drifting at the edges. Periods divide 10s so they loop."""
    specs = [
        # r, (cx, cy), waypoints, period
        (420, (140, 60), [(0, 0), (120, 50), (40, 120), (-60, 30)], 10),
        (380, (1150, 360), [(0, 0), (-130, -60), (-30, -110), (50, -30)], 10),
        (240, (1160, 30), [(0, 0), (-80, 50), (30, 70)], 5),
    ]
    out = []
    global _counter
    for r, (x, y), path, period in specs:
        n = len(path)
        frames = "".join(
            f"{i / n * 100:.2f}%{{transform:translate({dx}px,{dy}px)}}" for i, (dx, dy) in enumerate(path)
        )
        frames += f"100%{{transform:translate({path[0][0]}px,{path[0][1]}px)}}"
        _counter += 1
        name = f"b{_counter}"
        css_rules.append(f"@keyframes {name}{{{frames}}}")
        css_rules.append(f".{name}{{animation:{name} {period:.4f}s ease-in-out infinite}}")
        out.append(f'<circle class="{name}" cx="{x}" cy="{y}" r="{r}" fill="url(#gGlow)"/>')
    return "\n".join(out)


# ------------------------------------------------------------------- scenes

def scene_name():
    words = NAME.split()
    # each word rises on its own, so position them around the center by hand
    parts = []
    for i, (word, x, anchor) in enumerate(zip(words, [CX - 14, CX + 14], ["end", "start"])):
        cls = rise(0.6 + i * 0.08, 2.75 + i * 0.04, 140, 200)
        parts.append(
            f'<text class="hb {cls}" x="{x}" y="222" font-size="112" letter-spacing="-4.5" '
            f'text-anchor="{anchor}" fill="{INK}">{word}</text>'
        )
    sub = anim(
        [
            (1.05, tf(dy=10, op=0), EXPO_OUT),
            (1.55, tf(op=1), LINEAR),
            (2.6, tf(op=1), EASE_IN),
            (2.8, tf(dy=-6, op=0), LINEAR),
        ]
    )
    return (
        slot(110, 252, "".join(parts))
        + f'<text class="hm {sub}" x="{CX}" y="290" font-size="28" fill="{GRAY}" text-anchor="middle">{SUBTITLE}</text>'
    )


def scene_roll():
    label = anim(
        [
            (2.85, tf(dy=10, op=0), EXPO_OUT),
            (3.2, tf(op=1), LINEAR),
            (5.15, tf(op=1), EASE_IN),
            (5.35, tf(dy=-6, op=0), LINEAR),
        ]
    )
    timings = [(2.95, 3.75), (3.75, 4.55), (4.55, 5.35)]
    words = []
    for word, (t_in, t_out) in zip(ROLL_WORDS, timings):
        cls = rise(t_in, t_out, 150, 240, settle=0.4)
        words.append(
            f'<text class="hb {cls}" x="{CX}" y="268" font-size="108" letter-spacing="-4.5" '
            f'text-anchor="middle" fill="url(#gIce)">{word}</text>'
        )
    return (
        f'<text class="hm {label}" x="{CX}" y="148" font-size="32" fill="{GRAY}" text-anchor="middle" letter-spacing="1">{ALWAYS}</text>'
        + slot(160, 300, "".join(words))
    )


def scene_hero():
    line = rise(5.4, 7.05, 130, 200, settle=0.5)
    push = anim([(5.9, "transform:scale(1)", LINEAR), (6.8, "transform:scale(1.03)", LINEAR)], origin())
    spans = []
    for i, word in enumerate(HERO):
        t = 5.42 + i * 0.09
        cls = anim([(t, "fill-opacity:0", EXPO_OUT), (t + 0.25, "fill-opacity:1", LINEAR)])
        fill = ' fill="url(#gIce)"' if word == HERO_ACCENT else ""
        spans.append(f'<tspan class="{cls}"{fill}>{word}</tspan>')
    inner = (
        f'<g class="{push}"><g class="{line}"><text class="hb" x="{CX}" y="230" font-size="88" letter-spacing="-3.5" '
        f'text-anchor="middle" fill="{INK}">{" ".join(spans)}</text></g></g>'
    )
    return slot(120, 262, inner)


def scramble(text, revealed, rng):
    return "".join(
        c if c in " @" or i < revealed else rng.choice(SCRAMBLE_CHARS)
        for i, c in enumerate(text)
    )


def status_line(text, y, start, t_out, rng):
    """Rise into a slot while decode-scrambling, then hold."""
    frames_n, step = 8, 0.045
    parts = []
    for k in range(frames_n):
        revealed = round(len(text) * k / frames_n)
        t0 = start + k * step
        parts.append(
            f'<text class="hm {window(t0, t0 + step)}" x="{CX}" y="{y}" fill="{GRAY}">'
            f"{html.escape(scramble(text, revealed, rng))}</text>"
        )
    done = start + frames_n * step
    final_text = html.escape(text).replace("@", f'<tspan fill="{ICE_INK}">@</tspan>')
    parts.append(f'<text class="hm {window(done, LOOP)}" x="{CX}" y="{y}" fill="{INK}">{final_text}</text>')
    mover = rise(start, t_out, 60, y - 16, settle=0.35)
    return slot(y - 46, y + 16, f'<g class="{mover}">{"".join(parts)}</g>')


def scene_status():
    rng = random.Random(2027)
    lines = [
        status_line(text, y, start, t_out, rng)
        for text, y, start, t_out in zip(
            STATUS, [152, 216, 280], [7.1, 7.32, 7.54], [9.3, 9.36, 9.42]
        )
    ]
    return f'<g font-size="44" text-anchor="middle" letter-spacing="-1">{"".join(lines)}</g>'


# --------------------------------------------------------------------- build

def build():
    bg_glow = glow()
    scenes = scene_name() + scene_roll() + scene_hero() + scene_status()

    style = "\n".join(
        [
            font_face("IB", "inter-800.woff2", 800),
            font_face("IM", "inter-500.woff2", 500),
            ".hb{font-family:'IB',-apple-system,'Helvetica Neue',sans-serif;font-weight:800}",
            ".hm{font-family:'IM',-apple-system,'Helvetica Neue',sans-serif;font-weight:500}",
            *css_rules,
            "@media (prefers-reduced-motion:reduce){*{animation-play-state:paused!important}}",
        ]
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ayaan faisal: welcome to my github. always building, experimenting, vibecoding. you can just build things. student at uwaterloo, interning at tribalscale, seeking summer 2027 internships.">
<style>
{style}
</style>
<defs>
  <radialGradient id="gGlow"><stop offset="0" stop-color="{ICE}" stop-opacity=".42"/><stop offset=".5" stop-color="{ICE}" stop-opacity=".14"/><stop offset="1" stop-color="{ICE}" stop-opacity="0"/></radialGradient>
  <linearGradient id="gIce" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1c64c4"/><stop offset=".55" stop-color="{ICE_INK}"/><stop offset="1" stop-color="#6cc2f5"/></linearGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
{bg_glow}
{scenes}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="27.5" fill="none" stroke="{BORDER}"/>
</svg>
"""
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(svg)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(svg.encode()) / 1024:.1f} KB)")


if __name__ == "__main__":
    build()

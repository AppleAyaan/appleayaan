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

# palette: icy blue, white, black
BG = "#03060a"
ICE = "#9ad8ff"
PALE = "#e6f6ff"
DEEP = "#2f7fd0"
MUTED = "#8fa3b5"

# velocity-ramp easings
EXPO_OUT = "cubic-bezier(.16,1,.3,1)"
EASE_IN = "cubic-bezier(.7,0,.84,0)"
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


def window(start, end):
    """Hard on/off visibility between start and end (for decode frames)."""
    return anim([(0, "opacity:0", STEP), (start, "opacity:1", STEP), (end, "opacity:0", STEP)])


def font_face(family, file, weight):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return (
        f"@font-face{{font-family:'{family}';font-weight:{weight};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    )


# ---------------------------------------------------------------- background

def blobs():
    """Drifting ice-light blobs behind the glass. Periods divide 10s so they loop."""
    specs = [
        # gradient, r, path of (dx, dy) waypoints, period
        ("gIce", 340, (260, 120), [(0, 0), (160, 60), (60, 160), (-80, 40)], 10),
        ("gPale", 260, (1010, 260), [(0, 0), (-140, -70), (-40, -150), (60, -40)], 10),
        ("gDeep", 380, (720, 470), [(0, 0), (-120, -40), (80, -90)], 5),
        ("gIce", 200, (1120, 40), [(0, 0), (-90, 70), (40, 100)], 10 / 3),
        ("gWhite", 170, (520, 380), [(0, 0), (120, -60), (240, 10), (100, 50)], 10),
    ]
    out = []
    for grad, r, (x, y), path, period in specs:
        n = len(path)
        frames = "".join(
            f"{i / n * 100:.2f}%{{transform:translate({dx}px,{dy}px)}}" for i, (dx, dy) in enumerate(path)
        )
        frames += f"100%{{transform:translate({path[0][0]}px,{path[0][1]}px)}}"
        global _counter
        _counter += 1
        name = f"b{_counter}"
        css_rules.append(f"@keyframes {name}{{{frames}}}")
        css_rules.append(f".{name}{{animation:{name} {period:.4f}s ease-in-out infinite}}")
        out.append(f'<circle class="{name}" cx="{x}" cy="{y}" r="{r}" fill="url(#{grad})"/>')
    return "\n".join(out)


# beats: every scene cut punches the light and flashes the frame
BEATS = [0.8, 2.9, 3.7, 4.5, 5.4, 7.1, 9.2]


def beat_pulse():
    frames = [(0, "transform:scale(1)", LINEAR)]
    for b in BEATS:
        frames += [
            (b - 0.02, "transform:scale(1)", EXPO_OUT),
            (b + 0.05, "transform:scale(1.08)", EXPO_OUT),
            (b + 0.6, "transform:scale(1)", LINEAR),
        ]
    return anim(frames, f"transform-box:view-box;transform-origin:{CX}px {CY}px")


def flash():
    frames = [(0, "opacity:0", LINEAR)]
    for b, peak in [(0.8, 0.18), (2.9, 0.5), (5.4, 0.5), (7.1, 0.45), (9.2, 0.25)]:
        frames += [(b - 0.02, "opacity:0", LINEAR), (b, f"opacity:{peak}", EXPO_OUT), (b + 0.14, "opacity:0", LINEAR)]
    return anim(frames)


# ------------------------------------------------------------------- scenes

def scene_name():
    group = anim(
        [
            (0.8, tf(1.25, op=0), EXPO_OUT),
            (1.3, tf(1, op=1), LINEAR),
            (2.75, tf(1.035, op=1), EASE_IN),
            (2.9, tf(1.14, op=0), LINEAR),
        ],
        f"transform-box:view-box;transform-origin:{CX}px {CY}px",
    )
    sub = anim(
        [
            (1.45, tf(dy=14, op=0), EXPO_OUT),
            (1.95, tf(op=1), LINEAR),
            (2.75, tf(op=1), EASE_IN),
            (2.9, tf(op=0), LINEAR),
        ]
    )
    shine = anim([(1.25, "transform:translateX(-500px)", "cubic-bezier(.45,0,.2,1)"), (2.3, "transform:translateX(1500px)", LINEAR)])
    name_attrs = f'x="{CX}" y="222" font-size="104" letter-spacing="-4"'
    return f"""
<g class="{group}">
  <clipPath id="nameClip"><text {name_attrs} class="hb" text-anchor="middle">{NAME}</text></clipPath>
  <text {name_attrs} class="hb" text-anchor="middle" fill="url(#gText)">{NAME}</text>
  <g clip-path="url(#nameClip)"><g transform="skewX(-20)"><rect class="{shine}" x="-200" y="0" width="260" height="{H}" fill="url(#gShine)"/></g></g>
  <text class="hm {sub}" x="{CX}" y="282" font-size="28" fill="{MUTED}" text-anchor="middle" letter-spacing="1">{SUBTITLE}</text>
</g>"""


def scene_roll():
    label = anim(
        [
            (2.9, tf(dy=12, op=0), EXPO_OUT),
            (3.2, tf(op=1), LINEAR),
            (5.25, tf(op=1), EASE_IN),
            (5.4, tf(op=0), LINEAR),
        ]
    )
    origin = f"transform-box:view-box;transform-origin:{CX}px 240px"
    timings = [(3.0, 3.7), (3.7, 4.5), (4.5, 5.4)]
    words = []
    for i, (word, (t_in, t_out)) in enumerate(zip(ROLL_WORDS, timings)):
        last = i == len(ROLL_WORDS) - 1
        frames = [
            (t_in, tf(1.12, dy=120, op=0), EXPO_OUT),
            (t_in + 0.38, tf(1, op=1), LINEAR),
        ]
        if last:  # final word zooms out through the cut instead of rolling up
            frames += [(t_out - 0.15, tf(1.03, op=1), EASE_IN), (t_out, tf(1.16, op=0), LINEAR)]
        else:
            frames += [(t_out - 0.02, tf(1, op=1), EASE_IN), (t_out + 0.25, tf(0.94, dy=-120, op=0), LINEAR)]
        cls = anim(frames, origin)
        words.append(f'<text class="hb {cls}" x="{CX}" y="268" font-size="104" letter-spacing="-4" text-anchor="middle" fill="url(#gText)">{word}</text>')
    # reward flare when the last word lands
    t_in = timings[-1][0]
    flare = anim([(t_in + 0.3, "opacity:0", LINEAR), (t_in + 0.4, "opacity:.85", EXPO_OUT), (t_in + 0.8, "opacity:0", LINEAR)])
    words.append(f'<text class="hb {flare}" x="{CX}" y="268" font-size="104" letter-spacing="-4" text-anchor="middle" fill="#fff">{ROLL_WORDS[-1]}</text>')
    return f"""
<text class="hm {label}" x="{CX}" y="150" font-size="34" fill="{ICE}" text-anchor="middle" letter-spacing="6">{ALWAYS}</text>
<g clip-path="url(#rollClip)">
  {"".join(words)}
</g>"""


def scene_hero():
    group = anim(
        [
            (5.4, tf(1.3, op=0), EXPO_OUT),
            (5.5, tf(1.18, op=1), EXPO_OUT),
            (5.9, tf(1, op=1), LINEAR),
            (6.95, tf(1.045, op=1), EASE_IN),
            (7.1, tf(1.12, op=0), LINEAR),
        ],
        f"transform-box:view-box;transform-origin:{CX}px {CY}px",
    )
    spans = []
    for i, word in enumerate(HERO):
        t = 5.45 + i * 0.14
        cls = anim([(t, "fill-opacity:0", EXPO_OUT), (t + 0.14, "fill-opacity:1", LINEAR)])
        fill = ' fill="url(#gIceText)"' if word == HERO_ACCENT else ""
        spans.append(f'<tspan class="{cls}"{fill}>{word}</tspan>')
    return f"""
<g class="{group}">
  <text class="hb" x="{CX}" y="226" font-size="80" letter-spacing="-3" text-anchor="middle" fill="#fff">{" ".join(spans)}</text>
</g>"""


def scramble(text, revealed, rng):
    return "".join(
        c if c in " @" or i < revealed else rng.choice(SCRAMBLE_CHARS)
        for i, c in enumerate(text)
    )


def status_line(text, y, start, rng):
    """Decode-scramble a line in, then hold it with a brief RGB split."""
    frames_n, step = 8, 0.05
    parts = []
    for k in range(frames_n):
        revealed = round(len(text) * k / frames_n)
        t0 = start + k * step
        cls = window(t0, t0 + step)
        parts.append(f'<text class="hm {cls}" x="{CX}" y="{y}" fill="{PALE}">{html.escape(scramble(text, revealed, rng))}</text>')
    done = start + frames_n * step
    final = window(done, 9.1)
    at = f'<tspan fill="{ICE}">@</tspan>'
    final_text = html.escape(text).replace("@", at)
    parts.append(f'<text class="hm {final}" x="{CX}" y="{y}" fill="#fff">{final_text}</text>')
    for dx, color in [(-4, ICE), (4, "#ffffff")]:
        split = window(done, done + 0.12)
        parts.append(f'<text class="hm {split}" x="{CX + dx}" y="{y}" fill="{color}" fill-opacity=".45">{html.escape(text)}</text>')
    return "\n".join(parts)


def scene_status():
    rng = random.Random(2027)
    exit_cls = anim(
        [(9.05, tf(1, op=1), EASE_IN), (9.25, tf(1.05, op=0), LINEAR), (9.9, tf(1, op=0), STEP)],
        f"transform-box:view-box;transform-origin:{CX}px {CY}px",
    )
    lines = [
        status_line(text, y, start, rng)
        for text, y, start in zip(STATUS, [150, 214, 278], [7.15, 7.45, 7.75])
    ]
    return f"""
<g class="{exit_cls}" font-size="46" text-anchor="middle" letter-spacing="-1">
{chr(10).join(lines)}
</g>"""


def glass_sheen():
    return anim([(0.15, "transform:translateX(-700px)", "cubic-bezier(.45,0,.2,1)"), (1.5, "transform:translateX(1600px)", LINEAR)])


# --------------------------------------------------------------------- build

def build():
    pulse = beat_pulse()
    flash_cls = flash()
    sheen = glass_sheen()
    bg_blobs = blobs()
    scenes = scene_name() + scene_roll() + scene_hero() + scene_status()

    gx, gy, gw, gh, gr = 56, 40, W - 112, H - 80, 34
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
  <radialGradient id="gIce"><stop offset="0" stop-color="{ICE}" stop-opacity="1"/><stop offset=".45" stop-color="{ICE}" stop-opacity=".45"/><stop offset="1" stop-color="{ICE}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gPale"><stop offset="0" stop-color="{PALE}" stop-opacity=".75"/><stop offset=".5" stop-color="{PALE}" stop-opacity=".2"/><stop offset="1" stop-color="{PALE}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gWhite"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".5" stop-color="#fff" stop-opacity=".12"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <radialGradient id="gDeep"><stop offset="0" stop-color="{DEEP}" stop-opacity="1"/><stop offset=".5" stop-color="{DEEP}" stop-opacity=".45"/><stop offset="1" stop-color="{DEEP}" stop-opacity="0"/></radialGradient>
  <linearGradient id="gFrost" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".13"/><stop offset=".5" stop-color="#fff" stop-opacity=".04"/><stop offset="1" stop-color="#fff" stop-opacity=".08"/></linearGradient>
  <linearGradient id="gEdge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".7"/><stop offset=".3" stop-color="#fff" stop-opacity=".1"/><stop offset=".7" stop-color="{ICE}" stop-opacity=".08"/><stop offset="1" stop-color="{ICE}" stop-opacity=".55"/></linearGradient>
  <linearGradient id="gText" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff"/><stop offset=".55" stop-color="{PALE}"/><stop offset="1" stop-color="{ICE}"/></linearGradient>
  <linearGradient id="gIceText" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PALE}"/><stop offset="1" stop-color="{ICE}"/></linearGradient>
  <linearGradient id="gShine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="gSheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <radialGradient id="gVignette" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath>
  <clipPath id="glass"><rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="{gr}"/></clipPath>
  <clipPath id="rollClip"><rect x="{gx}" y="162" width="{gw}" height="150"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <g class="{pulse}">
{bg_blobs}
  </g>
  <rect width="{W}" height="{H}" fill="url(#gVignette)"/>

  <!-- liquid glass pane -->
  <rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="{gr}" fill="#060b12" fill-opacity=".3"/>
  <rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="{gr}" fill="url(#gFrost)"/>
  <g clip-path="url(#glass)"><g transform="skewX(-24)"><rect class="{sheen}" x="0" y="-100" width="420" height="{H + 200}" fill="url(#gSheen)"/></g></g>
  <rect x="{gx + 0.75}" y="{gy + 0.75}" width="{gw - 1.5}" height="{gh - 1.5}" rx="{gr}" fill="none" stroke="url(#gEdge)" stroke-width="1.5"/>
  <rect x="{gx + 3}" y="{gy + 3}" width="{gw - 6}" height="{gh - 6}" rx="{gr - 3}" fill="none" stroke="{ICE}" stroke-opacity=".12" stroke-width="1"/>
  <path d="M{gx + gr} {gy + 1.5} H{gx + gw * 0.45}" stroke="#fff" stroke-opacity=".55" stroke-width="1.5" stroke-linecap="round"/>

  <!-- scenes -->
{scenes}

  <rect class="{flash_cls}" width="{W}" height="{H}" fill="#eaf7ff"/>
</g>
</svg>
"""
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(svg)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(svg.encode()) / 1024:.1f} KB)")


if __name__ == "__main__":
    build()

#!/usr/bin/env python3
"""Generate assets/banner.svg, the animated README banner.

Animated SVG with no JS so it autoplays inside a GitHub README. Transforms
and opacity are CSS keyframes; blur is SMIL (<animate> on feGaussianBlur)
because Safari doesn't support CSS filter functions on SVG elements. Both
share one 10s clock starting at load; times below are in seconds.

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
HEADSHOT = Path(__file__).resolve().parent / "assets" / "headshot.jpg"
UW_CREST = Path(__file__).resolve().parent / "assets" / "uw-crest.png"
PROJECT_SHOTS = Path(__file__).resolve().parent / "assets" / "projects"

W, H = 1280, 300
CX, CY = W / 2, H / 2
LOOP = 12.0

# palette: apple light, icy blue accent
BG = "#fbfbfd"
INK = "#1d1d1f"
GRAY = "#86868b"
BORDER = "#e5e5ea"
ICE = "#9ad8ff"
ICE_INK = "#3a9be6"  # ice blue dark enough to read on white

# fast in, soft landing (CSS + matching SMIL keySplines)
EXPO_OUT = "cubic-bezier(.16,1,.3,1)"
EASE_IN = "cubic-bezier(.6,0,.9,.4)"
GLIDE = "cubic-bezier(.65,0,.35,1)"
LINEAR = "linear"
STEP = "step-end"
SPLINES = {EXPO_OUT: ".16 1 .3 1", EASE_IN: ".6 0 .9 .4", GLIDE: ".65 0 .35 1", LINEAR: "0 0 1 1"}

# emoji fall back to the viewer's system emoji font, like the rest of the README
EMOJI = "'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji'"

# scene copy
NAME = "ayaan faisal"
SUBTITLE = "welcome to my github 👋"
ALWAYS = "always"
ROLL_WORDS = [("building.", "🛠️"), ("experimenting.", "🧪"), ("tokenmaxxing.", "✨")]
HERO = ("you can just ", "build", " things.")
# (emoji, text, logo, text width in Inter 500 @ 36px with -0.6 tracking; measured
# with fontTools, update if the text changes)
STATUS = [
    ("🎓", "student @ uwaterloo", "uw", 322.8),
    ("💼", "interning @ tribalscale", "ts", 343.1),
    ("🔭", "seeking summer 2027 internships", None, 521.9),
]
EMOJI_W = 42  # approximate system emoji advance at 36px
LOGO_H = 30
# featured projects: (name, emoji, screenshot) taken from each repo's README
PROJECTS = [
    ("agora", "💰", "agora.jpg"),
    ("elenchus", "🧐", "elenchus.jpg"),
    ("geosify", "🏝️", "geosify.jpg"),
    ("watsmygpa", "👨‍🎓", "watsmygpa.jpg"),
]
CARD_W, CARD_H, CARD_GAP = 250, 156, 28

# end lockup: headshot + name as a logo. NAME_W is the rendered width of NAME
# in Instrument Serif at 116px (measured with fontTools; update if NAME changes)
NAME_W = 456
AVATAR_R = 72
LOCKUP_GAP = 32
NAME_Y = 172
SCRAMBLE_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789#%*/_-+=!?$"

css_rules = []
filters = []
_counter = 0


def uid(prefix):
    global _counter
    _counter += 1
    return f"{prefix}{_counter}"


def pct(t):
    return f"{t / LOOP * 100:.3f}%"


def pad(frames):
    """Hold the first and last values out to 0s and LOOP."""
    if frames[0][0] > 0:
        frames = [(0, frames[0][1], STEP)] + frames
    if frames[-1][0] < LOOP:
        frames = frames + [(LOOP, frames[-1][1], LINEAR)]
    return frames


def anim(frames, extra=""):
    """Register a CSS keyframe animation and return its class name.

    frames: list of (time_s, css_props, easing_into_next_frame).
    """
    name = uid("a")
    body = "".join(
        f"{pct(t)}{{{props};animation-timing-function:{ease}}}"
        for t, props, ease in pad(frames)
    )
    css_rules.append(f"@keyframes {name}{{{body}}}")
    css_rules.append(f".{name}{{animation:{name} {LOOP}s infinite;{extra}}}")
    return name


def blur(frames):
    """Register an animated blur filter and return a class that applies it.

    frames: list of (time_s, std_deviation, easing_into_next_frame).

    The filter is only attached (via CSS) while the blur amount is changing,
    i.e. during the transitions themselves; while content holds sharp, or sits
    hidden fully blurred, it gets filter:none. WebKit rasterizes filtered SVG
    content at low resolution, so leaving even a near-zero blur attached makes
    text soft on high-DPI phone screens.
    """
    fid = uid("f")
    frames = pad(frames)
    values = ";".join(f"{v:g}" for _, v, _ in frames)
    times = ";".join(f"{t / LOOP:.4f}" for t, _, _ in frames)
    splines = ";".join(SPLINES.get(e, SPLINES[LINEAR]) for _, _, e in frames[:-1])
    filters.append(
        f'<filter id="{fid}" x="-20%" y="-60%" width="140%" height="220%">'
        f'<feGaussianBlur stdDeviation="{frames[0][1]:g}">'
        f'<animate attributeName="stdDeviation" dur="{LOOP}s" repeatCount="indefinite" '
        f'values="{values}" keyTimes="{times}" calcMode="spline" keySplines="{splines}"/>'
        f"</feGaussianBlur></filter>"
    )
    toggle = [
        (t, f"filter:url(#{fid})" if v != frames[i + 1][1] else "filter:none", STEP)
        for i, (t, v, _) in enumerate(frames[:-1])
    ]
    return anim(toggle)


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


SHARP = 0.01  # stdDeviation 0 can disable rendering in some engines


def blur_fade(inner, t_in, t_out, y=CY, settle=0.5, exit=0.3, rise=18, amount=14):
    """Blur transition: drift up out of soft focus, hold sharp, blur away."""
    cls = anim(
        [
            (t_in, tf(1.03, dy=rise, op=0), EXPO_OUT),
            (t_in + settle, tf(1, op=1), LINEAR),
            (t_out - exit, tf(1, op=1), EASE_IN),
            (t_out, tf(0.99, dy=-rise * 0.7, op=0), STEP),
        ],
        origin(y),
    )
    fcls = blur(
        [
            (t_in, amount, EXPO_OUT),
            (t_in + settle, SHARP, LINEAR),
            (t_out - exit, SHARP, EASE_IN),
            (t_out, amount, STEP),
        ]
    )
    return f'<g class="{fcls}"><g class="{cls}">{inner}</g></g>'


def font_face(family, file, weight=400, style="normal"):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return (
        f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:{style};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    )


# ---------------------------------------------------------------- background

def glow():
    """Faint ice light drifting at the edges. Periods divide 10s so they loop."""
    specs = [
        # r, (cx, cy), waypoints, period
        (380, (140, 40), [(0, 0), (120, 40), (40, 90), (-60, 20)], 10),
        (340, (1150, 280), [(0, 0), (-130, -40), (-30, -80), (50, -20)], 10),
        (220, (1160, 20), [(0, 0), (-80, 40), (30, 50)], 5),
    ]
    out = []
    for r, (x, y), path, period in specs:
        n = len(path)
        frames = "".join(
            f"{i / n * 100:.2f}%{{transform:translate({dx}px,{dy}px)}}" for i, (dx, dy) in enumerate(path)
        )
        frames += f"100%{{transform:translate({path[0][0]}px,{path[0][1]}px)}}"
        name = uid("b")
        css_rules.append(f"@keyframes {name}{{{frames}}}")
        css_rules.append(f".{name}{{animation:{name} {period:.4f}s ease-in-out infinite}}")
        out.append(f'<circle class="{name}" cx="{x}" cy="{y}" r="{r}" fill="url(#gGlow)"/>')
    return "\n".join(out)


# ------------------------------------------------------------------- scenes

def scene_name():
    """The loop point: the name sits centered and sharp at 0s (and 10s).

    It blurs out at the cut, then returns at the end inside the headshot
    lockup and glides back to center, so the loop has no blank frame.
    """
    lock_dx = (2 * AVATAR_R + LOCKUP_GAP) / 2
    cls = anim(
        [
            (0, tf(1, op=1), STEP),
            (1.9, tf(1, op=1), EASE_IN),
            (2.2, tf(0.99, dy=-12, op=0), STEP),
            (10.3, tf(1.03, dx=lock_dx, dy=18, op=0), EXPO_OUT),
            (10.85, tf(1, dx=lock_dx, op=1), LINEAR),
            (11.4, tf(1, dx=lock_dx, op=1), GLIDE),
            (LOOP, tf(1, op=1), LINEAR),
        ],
        origin(142),
    )
    fcls = blur(
        [
            (0, SHARP, STEP),
            (1.9, SHARP, EASE_IN),
            (2.2, 14, STEP),
            (10.3, 14, EXPO_OUT),
            (10.85, SHARP, LINEAR),
        ]
    )
    name = (
        f'<g class="{fcls}"><g class="{cls}"><text class="serif" x="{CX}" y="{NAME_Y}" font-size="116" '
        f'letter-spacing="-1.5" text-anchor="middle" fill="{INK}">{NAME}</text></g></g>'
    )
    sub = f'<text class="sans" x="{CX}" y="226" font-size="24" fill="{GRAY}" text-anchor="middle">{SUBTITLE}</text>'
    return name + blur_fade(sub, 0.25, 2.15, y=217, rise=10, amount=8)


def scene_lockup():
    """Headshot blurs in beside the name, then dissolves as the name re-centers."""
    left = CX - (2 * AVATAR_R + LOCKUP_GAP + NAME_W) / 2
    hx, hy, r = left + AVATAR_R, 140, AVATAR_R
    cls = anim(
        [
            (10.25, tf(0.85, op=0), EXPO_OUT),
            (10.8, tf(1, op=1), LINEAR),
            (11.35, tf(1, op=1), GLIDE),
            (11.85, tf(0.8, dx=60, op=0), STEP),
        ],
        f"transform-box:view-box;transform-origin:{hx}px {hy}px",
    )
    fcls = blur([(10.25, 16, EXPO_OUT), (10.8, SHARP, LINEAR), (11.35, SHARP, GLIDE), (11.85, 16, STEP)])
    data = base64.b64encode(HEADSHOT.read_bytes()).decode()
    return (
        f'<clipPath id="avatar"><circle cx="{hx}" cy="{hy}" r="{r}"/></clipPath>'
        f'<g class="{fcls}"><g class="{cls}">'
        f'<image href="data:image/jpeg;base64,{data}" x="{hx - r}" y="{hy - r}" width="{2 * r}" height="{2 * r}" clip-path="url(#avatar)"/>'
        f'<circle cx="{hx}" cy="{hy}" r="{r - 0.5}" fill="none" stroke="{BORDER}"/></g></g>'
    )


def scene_roll():
    label = f'<text class="sans" x="{CX}" y="88" font-size="24" fill="{GRAY}" text-anchor="middle" letter-spacing="1">{ALWAYS}</text>'
    out = [blur_fade(label, 2.25, 4.65, y=80, rise=10, amount=8)]
    timings = [(2.3, 3.1), (3.05, 3.9), (3.85, 4.7)]
    for (word, emoji), (t_in, t_out) in zip(ROLL_WORDS, timings):
        text = (
            f'<text class="serif-i" x="{CX}" y="196" font-size="116" letter-spacing="-1.5" text-anchor="middle" fill="url(#gIce)">'
            f'{word} <tspan font-size="76">{emoji}</tspan></text>'
        )
        out.append(blur_fade(text, t_in, t_out, y=160, settle=0.45, exit=0.25, rise=22))
    return "".join(out)


def scene_hero():
    before, accent, after = HERO
    spans = (
        f'<tspan>{before}</tspan>'
        f'<tspan class="serif-i" fill="url(#gIce)">{accent}</tspan>'
        f'<tspan>{after}</tspan>'
    )
    push = anim([(5.3, "transform:scale(1)", LINEAR), (6.1, "transform:scale(1.025)", LINEAR)], origin())
    text = (
        f'<g class="{push}"><text class="serif" x="{CX}" y="180" font-size="104" letter-spacing="-1.2" '
        f'text-anchor="middle" fill="{INK}" xml:space="preserve">{spans}</text></g>'
    )
    return blur_fade(text, 4.75, 6.3, settle=0.55, amount=18)


def scramble(text, revealed, rng):
    return "".join(
        c if c in " @" or i < revealed else rng.choice(SCRAMBLE_CHARS)
        for i, c in enumerate(text)
    )


def logo(kind, x, y):
    """A logo LOGO_H tall with its bottom just under the text baseline. Returns (markup, width)."""
    top = y + 2 - LOGO_H
    if kind == "uw":
        w = round(LOGO_H * 84 / 96, 1)  # crest aspect ratio
        data = base64.b64encode(UW_CREST.read_bytes()).decode()
        return f'<image href="data:image/png;base64,{data}" x="{x}" y="{top}" width="{w}" height="{LOGO_H}"/>', w
    # tribalscale mark: yellow square with two corner brackets (200x200 source)
    k = LOGO_H / 200
    return (
        f'<g transform="translate({x} {top}) scale({k:.4f})">'
        '<rect width="200" height="200" rx="30" fill="#ffea00"/>'
        '<polygon points="100,45 154,45 154,99 140,99 140,59 100,59" fill="#000"/>'
        '<polygon points="45,100 58,100 58,140 99,140 99,154 45,154" fill="#000"/></g>',
        LOGO_H,
    )


def status_line(emoji, text, kind, text_w, y, start, t_out, rng):
    """Blur in while decode-scrambling, then pop the logo in after the text."""
    logo_w = 0 if kind is None else LOGO_H * (84 / 96 if kind == "uw" else 1)
    gap_e, gap_l = 12, 14 if kind else 0
    total = EMOJI_W + gap_e + text_w + gap_l + logo_w
    x_text = CX - total / 2 + EMOJI_W + gap_e
    frames_n, step = 8, 0.045
    parts = [f'<text class="sans" x="{x_text - gap_e}" y="{y}" text-anchor="end">{emoji}</text>']
    for k in range(frames_n):
        revealed = round(len(text) * k / frames_n)
        t0 = start + k * step
        parts.append(
            f'<text class="sans {window(t0, t0 + step)}" x="{x_text}" y="{y}" fill="{GRAY}">'
            f"{html.escape(scramble(text, revealed, rng))}</text>"
        )
    done = start + frames_n * step
    final_text = html.escape(text).replace("@", f'<tspan fill="{ICE_INK}">@</tspan>')
    parts.append(f'<text class="sans {window(done, t_out)}" x="{x_text}" y="{y}" fill="{INK}">{final_text}</text>')
    if kind:
        lx = x_text + text_w + gap_l
        mark, _ = logo(kind, lx, y)
        pop = anim(
            [(done, tf(0.6, op=0), EXPO_OUT), (done + 0.4, tf(1, op=1), LINEAR)],
            f"transform-box:view-box;transform-origin:{lx + logo_w / 2}px {y - LOGO_H / 2}px",
        )
        fcls = blur([(done, 8, EXPO_OUT), (done + 0.4, SHARP, LINEAR)])
        parts.append(f'<g class="{fcls}"><g class="{pop}">{mark}</g></g>')
    return blur_fade("".join(parts), start, t_out, y=y - 12, settle=0.4, rise=14, amount=10)


def scene_projects():
    """Four featured projects as screenshot cards, blurring in left to right."""
    left = CX - (4 * CARD_W + 3 * CARD_GAP) / 2
    top = 46
    push = anim([(6.8, "transform:scale(1)", LINEAR), (8.2, "transform:scale(1.02)", LINEAR)], origin())
    cards = []
    for i, (name, emoji, shot) in enumerate(PROJECTS):
        x = left + i * (CARD_W + CARD_GAP)
        cid = uid("c")
        data = base64.b64encode((PROJECT_SHOTS / shot).read_bytes()).decode()
        card = (
            f'<rect x="{x + 4}" y="{top + 8}" width="{CARD_W - 8}" height="{CARD_H}" rx="16" fill="#0b2a4a" fill-opacity=".07"/>'
            f'<clipPath id="{cid}"><rect x="{x}" y="{top}" width="{CARD_W}" height="{CARD_H}" rx="14"/></clipPath>'
            f'<image href="data:image/jpeg;base64,{data}" x="{x}" y="{top}" width="{CARD_W}" height="{CARD_H}" '
            f'preserveAspectRatio="xMidYMin slice" clip-path="url(#{cid})"/>'
            f'<rect x="{x + 0.5}" y="{top + 0.5}" width="{CARD_W - 1}" height="{CARD_H - 1}" rx="13.5" fill="none" stroke="{BORDER}"/>'
            f'<text class="serif" x="{x + CARD_W / 2}" y="{top + CARD_H + 46}" font-size="34" text-anchor="middle" fill="{INK}">'
            f'{name} <tspan font-size="24">{emoji}</tspan></text>'
        )
        t_in = 6.35 + i * 0.09
        cards.append(blur_fade(card, t_in, 8.2 + i * 0.03, y=top + CARD_H / 2, settle=0.5, rise=20, amount=12))
    return f'<g class="{push}">{"".join(cards)}</g>'


def scene_status():
    rng = random.Random(2027)
    lines = [
        status_line(emoji, text, kind, text_w, y, start, t_out, rng)
        for (emoji, text, kind, text_w), y, start, t_out in zip(
            STATUS, [100, 158, 216], [8.35, 8.5, 8.65], [10.1, 10.15, 10.2]
        )
    ]
    return f'<g font-size="36" letter-spacing="-.6">{"".join(lines)}</g>'


# --------------------------------------------------------------------- build

def build():
    bg_glow = glow()
    scenes = scene_name() + scene_roll() + scene_hero() + scene_projects() + scene_status() + scene_lockup()

    style = "\n".join(
        [
            font_face("IS", "instrument-serif-regular.woff2"),
            font_face("IS", "instrument-serif-italic.woff2", style="italic"),
            font_face("IM", "inter-500.woff2", 500),
            f".serif{{font-family:'IS',{EMOJI},Georgia,serif;font-weight:400}}",
            ".serif-i{font-style:italic}",
            f".serif-i:not(tspan){{font-family:'IS',{EMOJI},Georgia,serif;font-weight:400}}",
            f".sans{{font-family:'IM',{EMOJI},-apple-system,'Helvetica Neue',sans-serif;font-weight:500}}",
            *css_rules,
            "@media (prefers-reduced-motion:reduce){*{animation-play-state:paused!important}}",
        ]
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ayaan faisal: welcome to my github. always building, experimenting, tokenmaxxing. you can just build things. featured projects: agora, elenchus, geosify, watsmygpa. student at uwaterloo, interning at tribalscale, seeking summer 2027 internships.">
<style>
{style}
</style>
<defs>
  <radialGradient id="gGlow"><stop offset="0" stop-color="{ICE}" stop-opacity=".42"/><stop offset=".5" stop-color="{ICE}" stop-opacity=".14"/><stop offset="1" stop-color="{ICE}" stop-opacity="0"/></radialGradient>
  <linearGradient id="gIce" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1c64c4"/><stop offset=".55" stop-color="{ICE_INK}"/><stop offset="1" stop-color="#6cc2f5"/></linearGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="24"/></clipPath>
  {"".join(filters)}
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
{bg_glow}
{scenes}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="23.5" fill="none" stroke="{BORDER}"/>
</svg>
"""
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(svg)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(svg.encode()) / 1024:.1f} KB)")


if __name__ == "__main__":
    build()

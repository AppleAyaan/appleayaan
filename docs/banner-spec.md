# animated readme banner

The 12-second animated banner at the top of the profile README.

- **File:** `assets/banner.svg`, 1280×300, about 200 KB
- **Source:** `scripts/build_banner.py`. Edit the copy or timings there, then run `python3 scripts/build_banner.py`.
- **Format:** animated SVG with no JavaScript, so it autoplays and loops in a GitHub README. Transforms and opacity are CSS keyframes. Blur is SMIL (`<animate>` on `feGaussianBlur`), because Safari doesn't support CSS blur on SVG elements. Both run on the same 12s clock from load.
- **Embedded assets:** the fonts (woff2 subsets), the headshot (`scripts/assets/headshot.jpg`), the project screenshots (`scripts/assets/projects/`) and the UW crest (`scripts/assets/uw-crest.png`) are base64 data URIs, because an SVG inside `<img>` can't load external files. The TribalScale mark is drawn inline as vector shapes.

## brief

An Apple-style ad on a minimal profile: light, simple, clean, fast, with smooth motion.

- **feel:** an Apple product page cut fast, with editorial type and lots of white space.
- **motion:** blur transitions. Text drifts up out of soft focus while it fades in (about 0.5s, `cubic-bezier(.16,1,.3,1)`), holds sharp, then blurs away (about 0.3s ease-in). Logos pop in with a small blur once their line decodes.
- **type:** all lowercase. Instrument Serif for display text, with italic for the accent words, and Inter 500 for secondary lines.
- **emoji:** the viewer's system emoji font, the same way the rest of the README renders them.
- **background:** Apple off-white `#fbfbfd` with faint ice-blue light drifting at the edges, plus a hairline border and rounded corners.
- **palette:** ink `#1d1d1f`, gray `#86868b` and an ice-blue accent gradient `#1c64c4 → #3a9be6 → #6cc2f5`.

## timeline (12s loop)

| time | scene |
|---|---|
| 0.0–2.2s | **ayaan faisal** is already centered and sharp (the loop point). *welcome to my github 👋* blurs in underneath, then both blur out |
| 2.25–4.7s | *always* + a rolling italic word in ice gradient: **building. 🛠️** → **experimenting. 🧪** → **vibecoding. ✨** Each word blur-crossfades into the next |
| 4.75–6.3s | **you can just *build* things.** blurs in, slowly pushes in, then blurs out |
| 6.35–8.3s | featured projects: four screenshot cards (taken from each repo's README) blur in left to right, staggered 0.09s: **agora 💰 · elenchus 🧐 · geosify 🏝️ · watsmygpa 👨‍🎓**, with a slow push-in |
| 8.35–10.2s | status lines blur in staggered 0.15s, each decode-scrambling (gray noise → ink, 8 frames × 45ms); the @ is ice blue, and the logos pop in after the text: 🎓 student @ uwaterloo [crest] · 💼 interning @ tribalscale [mark] · 🔭 seeking summer 2027 internships |
| 10.25–11.35s | end lockup: the headshot (circle) blurs in beside the name, like a logo |
| 11.35–12.0s | the headshot dissolves and the name glides back to center, which is the frame at 0.0s, so there's no blank frame at the loop |

## notes

- **Blur filters are only attached while the blur amount is changing.** A CSS `filter:url(#f)` ↔ `none` toggle runs alongside each SMIL blur. WebKit (iOS Safari, the GitHub app) renders filtered SVG content at low resolution, so a filter left attached at near-zero blur made sharp text look soft on phones. Keeping it attached while content was hidden also caused a Chrome paint glitch in the top-left corner.
- Every animation shares one 12s clock. Times in the script are in seconds and are converted to keyframe percentages (CSS) or keyTimes (SMIL).
- The lockup and logo placement depend on measured text widths (`NAME_W` and the widths in `STATUS`). If you change that text, re-measure it with fontTools (see below) or the layout will drift off center. `EMOJI_W` is an estimate, because emoji widths vary slightly by OS.
- The glow drifts on its own independent cycles (10s and 5s), so it never restarts and doesn't need to line up with the 12s scene loop.
- The decode frames come from a fixed random seed, so rebuilds are reproducible.
- `prefers-reduced-motion` pauses the CSS motion.
- Fonts are licensed under OFL (see `scripts/fonts/OFL-*.txt`). The subsets only contain the characters the banner uses.

## history

- **v1:** dark "liquid glass" version. It was dropped because it didn't feel like an Apple ad.
- **v2:** light mode, Inter 800 and mask reveals, at 1280×400.
- **v3:** serif type, blur transitions, emoji, logos, the headshot lockup and a seamless loop, at 1280×300.
- **v4 (current):** a 2s featured-projects scene added, loop extended to 12s.

## regenerating fonts / measuring text

```sh
pip install fonttools brotli
# fonts (only if you need characters outside the current subsets)
curl -L -o IS.ttf https://github.com/google/fonts/raw/main/ofl/instrumentserif/InstrumentSerif-Regular.ttf
pyftsubset IS.ttf --text="abcdefghijklmnopqrstuvwxyz .,'" --flavor=woff2 \
  --layout-features='kern,liga' --output-file=scripts/fonts/instrument-serif-regular.woff2
# (same for InstrumentSerif-Italic.ttf; Inter: instance Inter[opsz,wght].ttf at wght=500 opsz=32 first)

# measure a string's width
python3 -c "
from fontTools.ttLib import TTFont
f=TTFont('scripts/fonts/inter-500.woff2'); cm=f.getBestCmap(); hm=f['hmtx']; u=f['head'].unitsPerEm
t='student @ uwaterloo'; print(sum(hm[cm[ord(c)]][0] for c in t)/u*36 - 0.6*(len(t)-1))"
```

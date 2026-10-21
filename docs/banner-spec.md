# animated readme banner

The 10-second animated banner at the top of the profile README.

- **File:** `assets/banner.svg`, 1280×400, about 34 KB
- **Source:** `scripts/build_banner.py`. Edit the copy or timings there, then run `python3 scripts/build_banner.py`.
- **Format:** pure CSS-animated SVG with no JavaScript, so it autoplays and loops in a GitHub README. Fonts (Inter 800 and 500) are subset and embedded as base64 woff2, because an SVG inside `<img>` can't load web fonts.

## brief

An Apple-style ad on a minimal profile: light, simple, clean, fast, with smooth motion.

- **feel:** an Apple product page cut fast. Lots of white space, big near-black type, and one accent color.
- **motion:** mask reveals. Each line rises up out of an invisible slot, holds, then exits upward through it. Entries take about 0.4–0.5s with a strong ease-out (`cubic-bezier(.16,1,.3,1)`) and exits about 0.28s with an ease-in. Each entry has a subtle 1.04× settle and the hero line slowly pushes in.
- **background:** Apple off-white `#fbfbfd` with faint ice-blue light drifting at the edges, plus a hairline border and rounded corners so it sits like a card on both GitHub themes.
- **palette:** ink `#1d1d1f`, gray `#86868b` and an ice-blue accent gradient `#1c64c4 → #3a9be6 → #6cc2f5`.
- **type:** all lowercase. Inter 800 for headlines and Inter 500 for secondary lines.

## timeline (10s loop)

| time | scene |
|---|---|
| 0.0–0.6s | empty canvas with drifting ice light |
| 0.6–2.8s | **ayaan faisal** rises in word by word, *welcome to my github* fades up in gray, then both exit upward |
| 2.85–5.35s | *always* + a rolling word in ice gradient: **building.** → **experimenting.** → **vibecoding.** Each word rises in and is pushed out by the next |
| 5.4–7.05s | **you can just build things.** rises in with the words fading left to right; **build** is in ice blue. slow push-in, then exit |
| 7.1–9.4s | status lines rise in staggered 0.22s, each decode-scrambling (gray noise → ink text, 8 frames × 45ms). the @ is ice blue: student @ uwaterloo · interning @ tribalscale · seeking summer 2027 internships |
| 9.4–10.0s | empty canvas, matching frame 0, so the loop is seamless |

## notes

- Every animation shares one 10s clock. Times in the script are in seconds and are converted to keyframe percentages.
- Text animates inside fixed clip slots (`slot()`), and the text moves while the window stays still. That's what produces the mask reveal.
- Glow drift periods divide 10s evenly (10s and 5s), so the background loops cleanly too.
- The decode frames come from a fixed random seed, so rebuilds are reproducible.
- `prefers-reduced-motion` pauses the animation.
- Inter is licensed under OFL (see `scripts/fonts/OFL.txt`). The subsets only include a–z, 0–9 and the symbols used by the scramble.

## history

- **v1:** dark "liquid glass" version. Black background, frosted pane, flash frames and an RGB split. It was dropped because it didn't feel like an Apple ad, so the banner moved to light mode.

## regenerating the fonts

Only needed if you add characters outside the current subset:

```sh
pip install fonttools brotli
curl -L -o Inter.ttf "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf"
for w in 500 800; do
  fonttools varLib.instancer Inter.ttf wght=$w opsz=32 -o inter-$w.ttf
  pyftsubset inter-$w.ttf --text='abcdefghijklmnopqrstuvwxyz0123456789 .@#%&*/<>_-+=!?$' \
    --flavor=woff2 --layout-features='kern,liga' --output-file=scripts/fonts/inter-$w.woff2
done
```

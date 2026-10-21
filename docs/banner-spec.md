# animated readme banner

The 10-second animated banner at the top of the profile README.

- **File:** `assets/banner.svg`, 1280×400, about 42 KB
- **Source:** `scripts/build_banner.py`. Edit the copy or timings there, then run `python3 scripts/build_banner.py`.
- **Format:** pure CSS-animated SVG with no JavaScript, so it autoplays and loops in a GitHub README. Fonts (Inter 800 and 500) are subset and embedded as base64 woff2, because an SVG inside `<img>` can't load web fonts.

## brief

An ad-style banner cut like a tiktok edit, on a minimal profile.

- **feel:** an Apple keynote cut like a tiktok edit. Moves are fast in, slow hold (velocity ramps), with zoom punches on the beats, flash frames on the cuts, a decode scramble and an RGB split.
- **background:** liquid glass. Icy light blobs drift behind a frosted glass pane with a bright refraction edge and a sheen that sweeps across.
- **palette:** icy blue `#9ad8ff`, pale ice `#e6f6ff`, white and black `#03060a`.
- **type:** all lowercase. Inter 800 for headlines and Inter 500 for secondary lines.

## timeline (10s loop)

| time | scene |
|---|---|
| 0.0–0.8s | empty glass; the sheen sweeps across the pane |
| 0.8–2.9s | **ayaan faisal** slams in (1.25× → 1×) and a shine passes through the letters. *welcome to my github* rises underneath. slow push-in, then a zoom-out cut |
| 2.9–5.4s | *always* + a rolling word in ice gradient: **building.** → **experimenting.** → **vibecoding.** Words roll up from a clipped window with a zoom punch. vibecoding gets a white flare, then zooms out through the cut |
| 5.4–7.1s | **you can just build things.** slams in word by word, with **build** in ice. slow push-in, then the cut |
| 7.1–9.2s | status lines decode-scramble in, staggered 0.3s, each with a 0.12s RGB split; the @ is ice blue: student @ uwaterloo · interning @ tribalscale · seeking summer 2027 internships |
| 9.2–10.0s | back to empty glass, matching frame 0, so the loop is seamless |

**beats:** 0.8, 2.9, 3.7, 4.5, 5.4, 7.1 and 9.2s. On each beat the background light pulses (1.08×), and the scene cuts also get a white flash frame.

## notes

- Every animation shares one 10s clock. Times in the script are in seconds and are converted to keyframe percentages.
- Blob drift periods divide 10s evenly (10s, 5s and 3.33s), so the background loops cleanly too.
- The decode frames come from a fixed random seed, so rebuilds are reproducible.
- Real backdrop blur isn't possible in SVG. The frost comes from a tinted pane over pre-softened radial gradients, which also keeps playback smooth.
- `prefers-reduced-motion` pauses the animation.
- Inter is licensed under OFL (see `scripts/fonts/OFL.txt`). The subsets only include a–z, 0–9 and the symbols used by the scramble.

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

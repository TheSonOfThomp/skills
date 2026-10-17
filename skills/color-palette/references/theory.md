# Color Theory Reference

The distilled research behind the generator's algorithm. Sources at the end.

## Why OKLCH, not HSL/RGB

- HSL lightness is a transform of screen RGB, not human vision: `hsl(60,100%,50%)` (yellow) and `hsl(240,100%,50%)` (blue) have identical HSL lightness but wildly different perceived brightness. Palettes stepped evenly in HSL lightness look right in a swatch row and fail in real UI — yellows too bright, blues too dark, and the 500 steps across hues don't feel related.
- HSL hue also drifts with lightness: `hsl(240,80%,20%)` and `hsl(240,80%,90%)` are not the same perceptual hue (the light one shifts ~18° toward purple). OKLCH hue is stable across the ramp.
- OKLCH (cylindrical form of Björn Ottosson's Oklab) gives L lightness, C chroma, H hue where equal numbers look equal. Native in CSS since Chrome 111 / Safari 15.4 / Firefox 113, so palettes ship as `oklch()` with hex fallbacks.
- This mirrors classical painting practice: darkening with black shifts hue cool, lightening with white shifts reds toward blue, and painters correct with an adjacent hue. OKLCH does the correction mathematically.

## The ramp algorithm

Given a base color at OKLCH `(L₀, C₀, H₀)`:

1. **Lightness bounds**: `minL = max(0.05, L₀ − 0.40)`, `maxL = min(0.95, L₀ + 0.40)`. Pure white/black have zero chroma room; never ramp to the extremes.
2. **Distribute steps** from `maxL` (label 50) to `minL` (label 950). Even L steps look even; UI palettes often want extra density at the light end (backgrounds, hovers, borders).
3. **Clamp chroma per step**: every `(L, H)` pair has a maximum displayable chroma in sRGB. `C_step = chromaPct × maxChroma(L, H)`. High-chroma bases *must* desaturate at the light and dark ends — this is correct gamut mapping, not a bug. Without it the browser clips, and browsers clip inconsistently.
4. **Optional hue drift**: constant H works well in OKLCH, but very light/dark colors perceptually shift (Bezold–Brücke). Up to ~16° drift light→dark compensates; turning dark yellows toward orange/brown is a taste decision, not a correction.

Step counts: Tailwind 11 (50→950), Radix 12, generic 9. Labels: 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950.

## Contrast anchors

WCAG 2 contrast follows OKLCH lightness closely, so contrast targets map to L values that hold for every hue:

| L | white text | black text |
|---|---|---|
| 0.95 | 1.1–1.2:1 | ~18:1 |
| 0.70 | 2.5–2.8:1 | 7.4–8.3:1 |
| 0.55 | 4.6–5.1:1 (AA) | 4.1–4.6:1 |
| 0.50 | 5.7–6.3:1 (AA) | 3.3–3.7:1 (AA large) |
| 0.30 | ~13.5:1 (AAA) | ~1.5:1 |

White body text passes 4.5:1 from L 0.55 down, black from L 0.60 up. WCAG AA: 4.5:1 normal text, 3:1 large text. APCA (Lc) is the emerging successor for text rendering.

## Multi-hue unification

Same L (equal perceived brightness) + same chroma **percentage** (not absolute chroma — max chroma differs per hue: red reaches ~0.25 at mid-L, blue ~0.18) at each step. This is Stripe's "uniform lightness curve" made mechanical: every hue follows the same perceptual-lightness curve, so contrast and visual weight are consistent across hues, and rules like "any two colors 5 levels apart pass small-text contrast" hold system-wide.

Chroma strategies, in increasing sophistication:
1. Same absolute chroma everywhere — breaks gamut for some hues.
2. Each hue at its own max — displays everywhere, unequal vividness.
3. **Shared gamut** (recommended default): the highest chroma *every* palette hue can display at that lightness. Downside: the most-constrained hue (blue near white, cyan mid-tone) limits the rest.

## Palette composition

- **Ramps first, then roles.** A palette is ramps + a role assignment, not loose swatches.
- **Radix-style step roles**: 1-2 app/subtle backgrounds · 3-5 component bg normal/hover/active · 6-8 borders (subtle/interactive/focus) · 9-10 solid bg + hover (9 = highest chroma, "purest") · 11-12 text low/high contrast.
- **Semantic aliases over raw scale names** (`--danger-500`, not `--red-500`); alias roles, not hues, when one scale serves several meanings.
- **Dark mode**: remap (flip lightest/darkest semantic assignments), never regenerate.
- **Hue selection**: traditional harmony (complementary 180°, analogous ±30°, triadic 120°) is a selection heuristic only. What matters perceptually is ΔE spacing at the steps actually used — hues 36° apart can become indistinguishable at high lightness/low chroma. Verify with cross-hue ΔE, not wheel geometry.

## Validation checklist

1. Monotonic lightness, near-constant adjacent-step ΔE (Oklab distance; the generator reports it).
2. Intended fg/bg pairs pass WCAG AA (4.5:1 / 3:1).
3. Cross-hue ΔE ≥ ~0.05 Oklab at steps 400+ (light steps always collide — they're near-white by design).
4. Colorblind simulation (Viénot protan/deutan/tritan): ~8% of men have red-green deficiency. Meaning must never ride on hue alone (WCAG 1.4.1) — pair color with shape, symbol, or label.
5. Test in real components, not swatch rows — HSL-era palettes look fine as swatches and fail in situ.

## Sources

- Björn Ottosson, [A perceptual color space for image processing (OKLab)](https://bottosson.github.io/posts/oklab/)
- [Colours: building an OKLCH palette](https://colours.viesual.net/oklch-color-palette) — shared-gamut strategy, contrast/L table, hue drift
- [oklch-skill palette generation](https://github.com/jakubkrehel/oklch-skill/blob/main/skills/oklch-skill/palette-generation.md) — the bounds/clamp algorithm implemented here
- Stripe, [Designing accessible color systems](https://stripe.com/blog/accessible-color-systems) — uniform lightness curve, contrast-by-construction, impossible colors
- [Radix Colors: understanding the scale](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale) — 12-step role assignment
- [Wikipedia: color theory](https://en.wikipedia.org/wiki/Color_theory) — hue shift in painting tints/shades, harmony history
- [ColorWiki](https://colorwiki.net), [Pantone pair recommender](https://pantonecolors.co/pair-recommender/) — harmony heuristics, WCAG tooling
- [W3C WCAG 1.4.1: use of color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html); [Matplotlib colormaps](https://matplotlib.org/stable/users/explain/colors/colormaps.html) (if data-viz ramps ever come up: sequential/diverging/qualitative, monotonic lightness, viridis family)

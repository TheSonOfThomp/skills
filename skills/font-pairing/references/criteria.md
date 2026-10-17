# Pairing Criteria

Deep-dive for the evaluation lens in the font-pairing skill. Synthesized from Tim Brown's *Combining Typefaces* (Five Simple Steps), Butterick's *Practical Typography*, and Adobe's font-pairing guidance.

## Principle: concord or contrast, never the murky middle

Fonts that are *too* similar look like a mistake — the canonical bad pair is Garamond set next to Sabon (two old-style faces with nearly identical skeletons). Serif + sans is the classic high-contrast pairing: maximize the stylistic distance between the two faces, then reconcile them at the detail level (proportion). If a candidate is a near-twin of the anchor, either reject it or go further in the contrast direction.

## Tim Brown's four zoom levels of graphic harmony

Evaluate every candidate at all four levels, from coarsest to finest:

1. **Texture (super-macro)** — Squint at blocks of text. Do the two faces have compatible "typographic color" (overall gray value / density) at the same point size? A large-x-height face set next to a small-x-height face produces visibly different densities — blocks of one will look darker and bigger than blocks of the other at equal sizes.
2. **Rhythm (macro/mid)** — Line length, leading, and word spacing should produce a compatible cadence. Long lines in one face and short in the other break the page rhythm.
3. **Proportion (micro)** — the single most concrete criterion. Compare:
   - **x-height** (the biggest texture driver)
   - **extender (ascender/descender) length**
   - **character width** (a condensed face against a normal-width face fails here even when everything else matches)
   - **aperture sizes** (open vs. closed terminals)
   - **stroke contrast** (variation between thick and thin strokes)

   Compatible proportions let shapes differ freely — "compatibility and similarity are not the same thing."
4. **Shape (super-micro)** — Geometry vs. calligraphy, angular vs. smooth contour. Two very different shapes can still pair if they share a construction philosophy (a square and a circle are both strict geometric forms).

## Practical criteria

- **Anchor first.** Pick the companion to serve the established anchor, not the reverse (Adobe). The anchor's proportions and hosting setup are constraints, not preferences.
- **Family breadth.** The companion must cover the roles the project needs — display, text, italic, ideally small caps / optical sizes — without weight gaps.
- **Licensing and hosting.** Must be legally licensable for web + desktop, and fit the project's pipeline (Adobe Fonts/Typekit kit, or self-hostable woff2 on the project CDN).
- **Rule of diminishing returns.** Two families is the comfortable maximum for most documents (Butterick). A third face needs a strong justification.

## X-height mismatch management

A companion with a notably smaller x-height than the anchor is not automatically disqualified — but the mismatch must be *managed*, not ignored:

- Set the smaller-x-height face ~5–10% larger in CSS (e.g. a `--font-<name>-size-adjust: 1.05–1.1` token) wherever it must optically align with the anchor.
- Check the weight/texture implication: at equal point sizes, unmanaged small-x-height blocks read lighter *and* smaller than the anchor's blocks.
- Record the management overhead in the evaluation table — it counts against the candidate's practicality score.

## Common pitfalls

| Pitfall | What it looks like | Guard |
|---|---|---|
| Murky middle | Two faces too similar to register as a choice (Garamond + Sabon) | Reject near-twins; pick concord *or* contrast, never in-between |
| Unmanaged x-height mismatch | Companion blocks look smaller/lighter at equal sizes | Optical size-adjust token (+5–10%) or eliminate |
| Unlicensable fonts | Perfect aesthetics, no legal web+desktop license (Apple Garamond — retired 2002, Apple-employee-only site license, unofficial downloads in a legal gray zone) | Licensing is a hard gate, checked before deep typographic investment |
| Borrowed brand equity | Nostalgia/corporate faces (Apple Garamond reads as "1990s Apple") read as someone else's voice, not the brand's | Prefer faces with their own identity |
| Width clash | A condensed companion against a normal-width anchor fails proportion even when x-heights match | Compare character width explicitly (it's the trap Apple Garamond fell into) |
| Serving the wrong master | Redesigning the anchor around the candidate | The companion adapts to the anchor's proportions, hosting, and weights |

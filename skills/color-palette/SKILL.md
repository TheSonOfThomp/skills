---
name: color-palette
description: Generate perceptually uniform color ramps and compose accessible color palettes in OKLCH. Builds gamut-clamped 9-12 step scales from base colors, unifies multiple hues at each step, and validates WCAG contrast and colorblind safety with a bundled script. Use when the user asks to create a color ramp, generate a color palette or color scale, expand a brand color into tints/shades, build design-system color tokens, or check a palette for contrast/colorblind accessibility.
inputs:
  - name: base_colors
    type: string
    required: true
    description: One or more base colors as #rrggbb or oklch(L C H) to expand into ramps
  - name: options
    type: string
    required: false
    description: Steps count, chroma percent, hue drift, dark mode, output format — freeform flags for the generator
  - name: context
    type: text
    required: false
    description: Brand intent, target surface (UI, design system, print), existing constraints, or an existing palette to audit
outputs:
  - name: palette_css
    type: file_path
    description: CSS custom-properties file with hex fallbacks and oklch values per scale step
  - name: report
    type: text
    description: In-chat validation report — contrast grades, ramp evenness, cross-hue separation, colorblind simulation
---

# Color Palette

Expand base colors into perceptually uniform ramps and compose them into a palette. All math is delegated to the bundled generator; this skill's judgment is in configuration and validation.

## Principles (why OKLCH)

- **Never generate ramps in HSL/RGB.** HSL lightness lies (same value ≠ same perceived brightness) and hue drifts as you tint/shade. Equal HSL lightness makes yellows look too bright, blues too dark.
- **OKLCH is the working space**: L (lightness), C (chroma), H (hue) — equal numbers look equal, and it's native CSS.
- **Chroma must be gamut-clamped per step.** High chroma is physically impossible at very light/dark steps; the generator reduces it rather than letting the browser clip.
- **One contrast anchor**: white text passes WCAG AA from L ≈ 0.55 down, black text from L ≈ 0.60 up. Mid-steps are placed around these targets.

Full theory and sources: [references/theory.md](references/theory.md)

## Workflow

### 1. Clarify the goal

Confirm with the user (skip what's already known): base color(s) or brand colors; step count (11 is standard, 9 lean, 12 if Radix-style roles needed); which hues the palette needs (brand + semantic: success/warning/danger/info + neutral); dark mode required?

### 2. Generate the ramps

```bash
cd "{skill_dir}/scripts" && python3 generate_ramp.py "#3b82f6" --steps 11 --chroma 90
# multi-hue palette: one invocation, comma-separated names
python3 generate_ramp.py "#3b82f6" "#e11d48" "#22c55e" --names blue,red,green --format css
```

Key flags: `--chroma N` (percent of per-step gamut max; 80-95 typical, higher = punchier), `--hue-drift D` (deliberate hue turn light→dark, e.g. dark yellows toward orange; only on request), `--cvd` (deutan-simulated hexes), `--format table|css|json`.

**Multi-hue rule**: generate all hues in ONE invocation so they share identical L and chroma-percentage at each step — this is what makes `blue-500` and `red-500` feel like siblings. Never regenerate one hue with different bounds.

### 3. Validate

Read the table output and check:

- [ ] Lightness monotonic, adjacent-step ΔE roughly constant (evenness column)
- [ ] Intended fg/bg step pairs pass WCAG AA (white text needs a step with `vs-white ≥ 4.5`; black text `vs-black ≥ 4.5`)
- [ ] Cross-hue ΔE warning absent (≥ 0.05 Oklab between same-step hues)
- [ ] With `--cvd`: deutan-simulated step colors still distinguishable at the steps used for meaning-carrying UI

If the user supplied an existing palette to audit, convert each step to OKLCH (`--format json` on a reconstruction, or convert manually) and check the same four points.

### 4. Compose the palette

- **Assign roles to steps** (Radix convention): 1-2 app backgrounds · 3-5 component bg (normal/hover/active) · 6-8 borders/focus · 9-10 solid bg and hover (step 9 = purest, highest-chroma) · 11-12 text (low/high contrast).
- **Alias semantically**: `--danger-500`, not `--red-500`, when a scale serves one meaning. One scale can back several aliases.
- **Dark mode = remap, don't regenerate**: keep the scale, flip semantic assignments (lightest step becomes darkest surface, text colors swap ends). Perceptual evenness in OKLCH makes the reversed mapping equally readable.

### 5. Deliver

Write the `--format css` output to a file (custom properties with hex fallbacks inside `@supports`), plus the validation report in chat. If a design system is the destination, suggest token naming (primitive scale + semantic alias tier).

## Common fixes

| Symptom | Fix |
|---|---|
| Steps 50/100 look washed out | Expected — chroma is physically limited near white; don't "fix" it by clamping |
| Hues look unequal in vividness | Same invocation for all hues; try `--chroma 80` |
| A 500-step fails contrast for white text | Accept it for large text/graphics, or drop mid-lightness (`--hue-drift` won't help; move the anchor) |
| Dark yellows read olive | Deliberate `--hue-drift 10-15` toward orange, or accept as brand taste |

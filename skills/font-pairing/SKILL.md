---
name: font-pairing
description: Research and select a typeface to pair with an established brand typeface (e.g. a serif to complement an existing sans). Profiles the anchor face, researches candidates across Typewolf/foundry/Adobe Fonts sources, evaluates them against Tim Brown's proportion criteria, and produces a sourced recommendation with licensing checks. Use when the user asks to pick, find, or choose a font pairing, select a companion typeface, or evaluate how well two typefaces work together.
inputs:
  - name: brief
    type: text
    required: true
    description: The pairing goal — which typeface is the anchor, what role the companion fills (serif, display, mono…), and any brand or design constraints
  - name: brand_context
    type: glob
    required: false
    description: Existing brand/typography files (font stacks, CSS tokens, brand docs) that reveal the anchor face, its weights, and its hosting setup
outputs:
  - name: recommendation
    type: file_path
    description: Pairing research write-up — anchor profile, candidate comparison table, ranked recommendation with sources and licensing path
  - name: summary
    type: text
    description: Concise verdict — primary pick, runner-up, and any eliminated candidates with the disqualifying reason
---

# Font Pairing

Select a companion typeface that serves the established **anchor** typeface — never the reverse. The deliverable is a researched, sourced recommendation, not a vibe.

## Workflow

### 1. Profile the anchor typeface

Build a table of the anchor (template in [references/templates.md](references/templates.md)): classification and lineage (designer, era, influences), x-height, apertures, stroke contrast, voice, and how it's deployed in the project (weights, self-hosted vs. webfont service). Pull from the foundry page, Adobe Fonts, and Typewolf.

The x-height and aperture row drives everything downstream — proportion matching is the single most concrete pairing criterion.

### 2. Set the pairing criteria

- **Concord or contrast, never the murky middle.** Two similar faces read as a mistake; either echo the anchor or oppose it decisively.
- **Tim Brown's four zoom levels** — texture, rhythm, proportion, shape — as the evaluation lens. Full criteria deep-dive in [references/criteria.md](references/criteria.md).
- **Practical gates:** legally licensable for web + desktop; hostable in the project's pipeline; family breadth covers the needed roles (text, display, italic, small caps) without weight gaps. Two families is the comfortable maximum for most projects.

### 3. Research candidates

Gather 3–4 candidates via web research, spanning the contrast range (one concordant echo, one maximal contrast, and typically one near-miss worth eliminating explicitly):

- **Typewolf** — the anchor's page lists *suggested pairings* and *Fonts In Use*-style observed real-world pairs. Highest-signal starting point.
- **Foundry pages** — the designer's stated intent (e.g. "drawn to pair with a geometric grotesk") is the strongest shape evidence.
- **Adobe Fonts / MyFonts** — licensing availability, family breadth, optical sizes.
- **Fonts In Use** — precedent pairs on real sites.

### 4. Evaluate each candidate

Score every candidate against the anchor on: x-height, aperture/texture, stroke contrast, shape philosophy, character width, family breadth, licensing. Use the comparison table template in [references/templates.md](references/templates.md). Note the *management cost* of any mismatch (e.g. a small-x-height companion needs +5–10% optical size adjustment).

### 5. Verify licensing — hard gate

A candidate that cannot be licensed for web + desktop is **eliminated regardless of aesthetics** (the canonical case: Apple Garamond — held under a retired Apple-only site license, only unofficial downloads exist). Prefer candidates that fit the project's existing pipeline (e.g. Adobe Fonts/Typekit or self-hosted woff2).

### 6. Write the recommendation

Follow the write-up format in [references/templates.md](references/templates.md): anchor profile → comparison table → primary recommendation with rationale → alternative for a different design direction → eliminated candidates with reasons → next steps (mockup, size-adjust token, license path) → full source list. End with a concise verdict summary to the user.

## Common pitfalls

Covered in [references/criteria.md](references/criteria.md#common-pitfalls): murky-middle pairs, unmanaged x-height mismatch, unlicensable fonts, borrowed brand equity (nostalgia faces), and width-contrast clashes.

# Templates

Copy-paste templates for the font-pairing skill deliverables.

## 1. Anchor typeface profile

```markdown
## <Anchor name> — the anchor typeface

| Attribute | Value |
|---|---|
| Designer / era | <name, year, nationality/school> |
| Classification | <e.g. geometric sans with humanist influences> |
| Stated influences | <what the designer/foundry says it derives from> |
| X-height | <large / small / ~fraction of cap height> |
| Apertures | <open / closed> |
| Stroke contrast | <high / low / optical vs. metrical modulation> |
| Voice | <the 2–3 adjectives it projects> |
| In this project | <weights in use, self-hosted path or webfont service> |

Sources: [foundry](url) · [Adobe Fonts](url) · [Typewolf](url)
```

## 2. Candidate comparison table

One table per candidate — the row labels double as the evaluation checklist. Score against the anchor profile, not in the abstract.

```markdown
### <Candidate> — <designer>, <year> (<foundry>) — ⭐ Recommended | Runner-up | ❌ Eliminate

| Criterion | Assessment |
|---|---|
| Classification | <e.g. transitional serif — where it sits stylistically> |
| X-height | <vs. the anchor: match / gap + management cost> |
| Aperture / texture | <how its blocks read beside the anchor at equal size> |
| Stroke contrast | <compatible / clashing with the anchor's> |
| Character width | <normal / condensed / extended vs. the anchor> |
| Shape philosophy | <shares / opposes the anchor's construction — and is that concord or contrast?> |
| Family breadth | <weights, widths, italics, small caps, optical sizes vs. needed roles> |
| Precedent | <Typewolf suggested pairing? observed real-world pairs?> |
| Licensing | <Adobe Fonts / MyFonts / foundry; web + desktop; self-hostable?> |

**Why it works:** <2–3 sentences tied to the zoom levels — texture, proportion, shape.>
**Risk:** <the honest downside — warmth, bookishness, management overhead, association.>
```

## 3. Recommendation write-up

```markdown
## Recommendation

1. **Primary: <typeface>.** <Proportion match, shape philosophy, family breadth, licensing fit — in that order of strength.>
2. **Alternative: <typeface>** if the design direction wants <other quality> — accepting <named management overhead, e.g. ~5–10% optical size adjustment>.
3. **Do not use <eliminated typeface>** — <licensing blocker and/or proportional mismatch>.

### Suggested next steps
- Mock up the top candidates beside the anchor at equal sizes (the texture/squint test).
- If a size-adjust token is needed, define it (e.g. `--font-<name>-size-adjust: 1.05`).
- Confirm the license path: webfont service vs. self-hosted woff2 matching the anchor's setup.

## Sources
- <Anchor>: [foundry](url) · [Adobe Fonts](url) · [Typewolf](url) (<notable suggested/observed pairings>)
- Pairing theory: Tim Brown, *Combining Typefaces* · Butterick, *Practical Typography*
- <Candidate 1>: [source](url) · [source](url)
- <Candidate 2>: ...
```

## 4. Verdict summary

End with the concise console/app verdict:

```
## Pairing Research Complete

Anchor   : <anchor> (<classification>)
Primary  : <typeface> — <one-line rationale>
Alt      : <typeface> — <one-line tradeoff>
Rejected : <typeface> — <disqualifying reason>
Details  : <path to the write-up>
```

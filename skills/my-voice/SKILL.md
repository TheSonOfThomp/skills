---
name: my-voice
description: Draft or rewrite communications (Slack messages, PR comments, Asana comments, email) in the user's personal voice, using a stored voice profile currently mined from their iMessage TXT archive. Use when the user asks to write/rewrite a message in their voice, draft a Slack post, PR comment, or email "as me", or invokes /my-voice. Build/refresh the profile with /my-voice build.
inputs:
  - name: intent_or_draft
    type: text
    required: false
    description: Intent/bullets to draft from, or prose to rewrite in voice; absent for build/refresh
  - name: mode
    type: enum
    required: false
    description: One of draft (default), build, or refresh
outputs:
  - name: drafted_text
    type: text
    description: Paste-ready message in the user's voice (text only, never sent)
  - name: voice_profile
    type: file_path
    description: "{vault_references}/voice-profile.md written/overwritten on build or refresh"
---

> **Configuration**: Before running, read `{vault_references}/config.json` and substitute all `{config_key}` placeholders with the values defined there.

# My Voice

Write communications that sound like the user, not like an LLM. A stored **voice profile** at `{vault_references}/voice-profile.md` captures per-medium style; drafting reads the profile and applies it. Output is always paste-ready text — never send anything directly.

When the profile contains both inferred baseline traits and explicit user-written professional/work guidance, treat the explicit user-written guidance as authoritative for work prose.

**Commands:** `/my-voice <intent or draft>` · `/my-voice build` · `/my-voice refresh`

**As a sub-step**: when another skill is about to present or publish outward-facing prose (per the global Voice rule in CLAUDE.md), apply the profile inline — read the matching medium section and restyle the text before showing it; skip the interactive draft workflow ceremony.

## build (`/my-voice build`, also `refresh`)

Mine authored communications and compile the profile:

1. **iMessage TXT archive** (current source of truth): extract only sent text messages with:
   ```bash
   cd "{vault_root}" && node tools/lib/extract-imessage-sent.ts \
     --archive ~/Archives/imessage-export-YYYY-MM-DD-txt \
     --sender "Me" \
     --format jsonl \
     --half-life-days 365
   ```
   Use this as the basis of the profile for now. Weight recent messages more strongly than old ones; use old messages as baseline habits, not equal votes. If multiple archive directories exist, prefer the newest one or ask the user which export to use.
2. **Analyze** the extracted corpus across dimensions: directness/hedging, sentence length/rhythm, greetings & sign-offs, emoji/punctuation habits, recurring phrases and vocabulary, question style, humor style, how appreciation is expressed, and how emotionally serious messages expand in length and specificity.
   - Prefer recent samples for current voice.
   - Use older samples for durable baseline traits.
   - Treat exporter/system text as noise; focus on authored message content only.
3. **Write the profile** to `{vault_references}/voice-profile.md`: keep universal traits plus medium sections (Slack / PR review / Asana / email), but make it explicit that the current profile is inferred from iMessage only unless the user has added stronger hand-written professional guidance. Frontmatter: `built: YYYY-MM-DD`, `sources: [imessage]`. Exclude anything sensitive from examples.
4. `refresh` re-runs the same flow and overwrites; preserve any `## Manual notes` section the user added by hand.

## draft (`/my-voice <input>`)

1. Read `{vault_references}/voice-profile.md`. If missing, offer to run `build` first (or proceed with a one-off live sample if the user declines).
2. Determine the **medium** (Slack/PR/Asana/email) from the request or ask; determine the **mode**:
   - Input is intent/bullets → draft from scratch.
   - Input is prose draft → rewrite into the user's voice, preserving meaning and technical content.
3. Apply the matching profile section.
   - For work prose, prefer the explicit professional/work sections in `voice-profile.md` over the inferred casual baseline.
   - Use the iMessage-derived baseline mainly for universal traits like warmth, brevity, rhythm, and recurring phrasing.
   - Audience matters: note if the target (exec, teammate, public channel) suggests a register shift, but stay in voice.
4. Present the draft in a fenced block (paste-ready). Iterate on feedback. If the profile felt wrong somewhere, note it and suggest a `refresh` or a `## Manual notes` correction.

## Guardrails

- Never post/send to Slack, GitHub, Asana, or email — output text only.
- The profile contains excerpts of internal communications; it lives in the private vault and must never go into shared bundles.
- Don't caricature: the profile is a baseline, not a costume. When the user's draft already sounds right, change less.

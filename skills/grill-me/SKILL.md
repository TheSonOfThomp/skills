---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
inputs:
  - name: context
    type: text
    required: false
    description: Live conversation — plan/design details gathered before interactive answers
outputs:
  - name: shared_understanding
    type: text
    description: Resolved decision tree surfaced through the interview, with recommended answers per question
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

Keep each question to a single decision — don't bundle independent decisions into one prompt. If the user pushes back or wants to clarify rather than answer, engage that first, then re-pose once resolved.

If the user revises an earlier answer, treat every later decision that depended on it as re-opened — re-pose those downstream questions rather than silently keeping now-stale answers.

If the possible responses suit, use the client's AskUser UI to ask single-select or multiple chouce questions.

**First, suppress the post-skill Stop hook for the duration of the interview.** This skill is
multi-turn — it stops after every question — and the `post-skill-sequence` Stop hook would otherwise
fire its reminder after each one. Drop the suppression sentinel before interviewing:

```bash
node -e 'const fs=require("fs"),os=require("os"),p=require("path");fs.writeFileSync(p.join(os.tmpdir(),"uxe-post-skill-suppress"),"grill-me in progress\n")'
```

Remove it when the interview concludes (shared understanding reached, or the user moves on to
implementation), so the normal `/skill-review → /skill-eval → /wiki` sequence runs once at the end:

```bash
node -e 'const fs=require("fs"),os=require("os"),p=require("path");fs.rmSync(p.join(os.tmpdir(),"uxe-post-skill-suppress"),{force:true})'
```

Use the initial prompt and the live conversation to gather enough context to begin grilling. If
context is incomplete, ask a substantive clarifying question rather than using a placeholder prompt.

If a question can be answered by exploring the codebase, explore the codebase instead. This applies to the *recommendations* too: before asserting a codebase-checkable fact as the basis for a recommended answer — especially a negative claim ("X isn't generated/shipped/tracked", "there's no tool for Y") — verify it against the code first. Don't make the user catch a wrong premise.

When a recommendation depends on an external tool, command, or renderer actually *working* (e.g. "use Marp", "this CLI will do it"), or on a generated artifact being *good enough* (e.g. "this query returns a strong answer"), verify it by actually running it before recommending — don't wait for the user to demand proof. A recommendation that rests on an unproven "it'll work" is a premise the user shouldn't have to catch.

This includes **governing constraints**, not just code: before recommending anything that touches integrations, auth, credentials, external services, or conventions, check the project's binding instructions (CLAUDE.md, `references/config.json`, established skill patterns) so a recommendation can't contradict a rule the user already set. If a recommendation would later need walking back because of such a constraint, you should have surfaced the constraint in the question itself.

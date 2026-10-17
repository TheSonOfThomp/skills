---
name: skills-sync
description: Links every skill from this skills repo (and any extra skill folders, such as an Obsidian vault's skills/) into ~/.claude/skills and ~/.codex/skills, one symlink per skill, so new skills are available immediately without manual wiring. Use when skills are out of sync, after a fresh machine setup, or when asked to "sync skills", "fix skill symlinks", or "link skills dir".
inputs:
  - name: sources
    type: dir_path
    required: false
    description: Extra skill folders to link besides this repo's skills/ (e.g. a vault's skills/)
outputs:
  - name: symlinks
    type: dir_path
    description: ~/.claude/skills and ~/.codex/skills populated with one symlink per skill (side effect)
---

# skills-sync

Skills come from more than one place: this repo's `skills/` folder, and optionally other folders such as a vault's `skills/`. Each target directory is a real directory holding one symlink per skill, so it can show skills from every source at once and keep tool-managed content (like Codex's `.system/`) untouched.

| Target | Managed here | Why |
|---|---|---|
| `~/.claude/skills/` | yes | Claude Code reads it |
| `~/.codex/skills/` | yes | Codex reads it, alongside its built-in `.system/` skills |
| `~/.agents/skills/` | no | pi reads it, and pi installs this repo as a package (`/thesonofthomp:init`), so linking these skills here too would duplicate them |

## Steps

1. **Find the sources.** This repo's `skills/` folder is always first. If the user keeps other skills in a vault, read its `references/config.json` and add `vault_skills` as a second `--source`. Earlier sources win when two have a skill with the same name.

2. **Preview** from this skill's directory:
   ```bash
   node scripts/sync.mjs --source <repo>/skills --source "<vault_skills>" --dry-run
   ```
   Show the user the summary. A target that is still a whole-directory symlink (the old layout) is replaced with a real directory; the folder it pointed at is not touched.

3. **Run** the same command without `--dry-run`.

4. **Report** the per-target counts, any `conflict` lines (real files, or links to somewhere outside the sources, which are left alone) and any `shadowed` lines (the same name in two sources).

## Notes

- Skills installed with `npx skills add` are already linked by that CLI; this skill is for working from a clone, or for combining a clone with other folders.
- The script only removes symlinks that point into one of the sources and whose skill is gone. It never deletes real files or directories.
- It is idempotent: safe to run any time, and after adding or removing a skill.
- Pass `--target DIR` (repeatable) to link into other directories instead of the defaults.

# @thesonofthomp/skills

Agent skills by [@thesonofthomp](https://github.com/TheSonOfThomp), in the [Agent Skills](https://agentskills.io/specification) format. They work in [pi](https://pi.dev), Claude Code and Codex.

| Skill | What it does |
|---|---|
| `color-palette` | Builds perceptually uniform OKLCH colour ramps and accessible palettes, with a bundled contrast and colourblind check |
| `font-pairing` | Researches and recommends a typeface to pair with an existing brand face |
| `git-actions` | Git and `gh` workflows: commits, branches, PRs, rebases, conflicts, with safety checks for destructive commands |
| `grill-me` | Interviews you about a plan until every branch of the decision tree is resolved |
| `grill-with-docs` | A grilling session that also updates `CONTEXT.md` and ADRs as decisions settle |
| `my-voice` | Drafts or rewrites messages in your voice from a stored voice profile |
| `safari-control` | Drives Safari on macOS with AppleScript and `do JavaScript` |
| `skills-sync` | Links skills from this repo (and other folders) into `~/.claude/skills` and `~/.codex/skills` |
| `vscode-context` | Lists the files open in the VS Code window around the terminal and reads the ones you pick |
| `wayfinder` | Plans work too big for one session as a map of decision tickets on your issue tracker, resolved one at a time |

`grill-me`, `grill-with-docs` and `wayfinder` are adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT).

## Install

### pi

[`@thesonofthomp/pi-config`](https://github.com/TheSonOfThomp/pi-config)'s `/thesonofthomp:init` command installs these automatically. To install them on their own:

```bash
pi install git:github.com/TheSonOfThomp/skills
```

Pin a release with `@vX.Y.Z`. Use `pi config` to turn individual skills off.

### Claude Code and Codex

Clone the repo, then link every skill into `~/.claude/skills` and `~/.codex/skills`:

```bash
git clone https://github.com/TheSonOfThomp/skills ~/Documents/GitHub/skills
node ~/Documents/GitHub/skills/skills/skills-sync/scripts/sync.mjs --dry-run
node ~/Documents/GitHub/skills/skills/skills-sync/scripts/sync.mjs
```

Add `--source <dir>` (after this repo's `skills/` folder) to link skills from other folders too, such as an Obsidian vault's `skills/`. The script only creates and removes its own symlinks; it never deletes real files.

## Development

```bash
npm test          # checks every SKILL.md and the sync script
npm run changeset # describe a change
npm run version   # bump the version from the pending changesets
```

Tag releases as `vX.Y.Z` after `npm run version`.

## License

MIT. See [LICENSE](LICENSE).

# @thesonofthomp/skills

Agent skills by [@thesonofthomp](https://github.com/TheSonOfThomp), in the [Agent Skills](https://agentskills.io/specification) format. They work in [pi](https://pi.dev), Claude Code and Codex.

| Skill | What it does |
|---|---|
| `color-palette` | Builds perceptually uniform OKLCH colour ramps and accessible palettes, with a bundled contrast and colourblind check |
| `ebay-search` | Searches and compares current eBay listings with useful filters and visible listing details |
| `font-pairing` | Researches and recommends a typeface to pair with an existing brand face |
| `git-actions` | Git and `gh` workflows: commits, branches, PRs, rebases, conflicts, with safety checks for destructive commands |
| `grill-me` | Interviews you about a plan until every branch of the decision tree is resolved |
| `grill-with-docs` | A grilling session that also updates `CONTEXT.md` and ADRs as decisions settle |
| `my-voice` | Drafts or rewrites messages in your voice from a stored voice profile |
| `safari-control` | Drives Safari on macOS with AppleScript and `do JavaScript` |
| `skills-sync` | Links skills from this repo (and other folders) into `~/.claude/skills` and `~/.agents/skills` |
| `vscode-context` | Lists the files open in the VS Code window around the terminal and reads the ones you pick |
| `wayfinder` | Plans work too big for one session as a map of decision tickets on your issue tracker, resolved one at a time |

`grill-me`, `grill-with-docs` and `wayfinder` are adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT).

## Install

Install with the [`skills` CLI](https://skills.sh):

```bash
npx skills add TheSonOfThomp/skills --list            # see what's in the repo
npx skills add TheSonOfThomp/skills -g --skill '*'    # all skills, for your user
npx skills add TheSonOfThomp/skills --skill grill-me  # one skill, for the current project
```

It asks which agents to install for (`--agent claude-code codex pi` skips the question). Global installs are copied to `~/.agents/skills`, which pi and Codex read directly, and symlinked into each other agent's folder (such as `~/.claude/skills`). `npx skills update` pulls new versions.

If `~/.agents/skills` is a symlink (for example to a synced vault folder), `npx skills -g` writes into the folder it points to.

### pi

[`@thesonofthomp/pi-config`](https://github.com/TheSonOfThomp/pi-config)'s `/thesonofthomp:init` command installs these with `npx skills add … --global --agent pi`, skipping any already in `~/.agents/skills`.

The repo is also a pi package (`pi install git:github.com/TheSonOfThomp/skills`), but don't use both: pi reads `~/.agents/skills` too, and would load each skill twice.

### From a clone

To work on the skills and use your edits straight away, clone the repo and link every skill into `~/.claude/skills` and `~/.agents/skills`:

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

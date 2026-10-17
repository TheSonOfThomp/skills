---
name: git-actions
description: Git workflow specialist covering commits, branches, PRs, merges, rebases, conflict resolution, log inspection, stashing, tagging, and safety checks for destructive operations. Use whenever the user wants to perform any git or GitHub CLI (gh) operation.
inputs:
  - type: none
outputs:
  - type: none
---
# Git workflow

## Core principles

- Prefer safe, reversible operations. Confirm before destructive actions (force-push, reset --hard, branch -D, clean -f).
- Never skip hooks (--no-verify) unless the user explicitly asks.
- Never amend published commits unless explicitly asked.
- Stage specific files by name; avoid `git add -A` or `git add .` unless the user confirms.
- Never commit changes the user did not explicitly request.
- Never push unless the user explicitly asks.
- When in doubt about scope, ask before acting.

## Commit workflow

When asked to commit:
1. Run `git status` (never with -uall) and `git diff` in parallel to understand current state.
2. Run `git log --oneline -10` to match existing commit message style.
3. Stage only the files relevant to the request.
4. Write a concise commit message focused on *why*, not *what*. Pass via HEREDOC to preserve formatting.
5. After committing, run `git status` to verify success.
6. If a pre-commit hook fails: fix the issue, re-stage, and create a NEW commit — never amend.

## Branch workflow

- Create branches from the appropriate base (usually `main` or as directed).
- Use descriptive, hyphenated names.
- After creating a branch, confirm the user is on it before proceeding.

## PR workflow

When asked to create a PR:
1. Check current branch vs remote: `git status`, `git log`, `git diff [base]...HEAD`.
2. Push to remote with `-u` if not yet tracking.
3. Use `gh pr create` with a clear title (under 70 chars) and a structured body via HEREDOC:
   ```bash
   gh pr create --title "the pr title" --body "$(cat <<'EOF'
   ## Summary
   - bullet points

   ## Test plan
   - [ ] checklist items
   EOF
   )"
   ```
4. Return the PR URL.

When asked to comment on a PR:
- Use `gh pr comment <number-or-URL> --body "..."` to post a top-level comment.
- For inline review comments on specific lines, use `gh api` with the pulls review endpoint, or `gh pr review --comment -F -` piped from a HEREDOC.
- To request changes or approve: `gh pr review <number> --approve` / `--request-changes --body "..."`.
- Always confirm the PR number or URL before posting — comments cannot be unsent.

When asked to view or inspect a PR:
- `gh pr view <number>` — summary, status, checks.
- `gh pr checks <number>` — CI status for all jobs.
- `gh pr diff <number>` — full diff.
- `gh api repos/{owner}/{repo}/pulls/<number>/comments` — inline review comments.

## Merge / rebase

- Prefer `git merge` for integrating shared branches; prefer `git rebase` for cleaning up local history before PR.
- For interactive rebase, describe the plan and confirm before executing (non-interactive `-i` is not available in this environment — use explicit squash/fixup commits instead).
- When resolving conflicts: show the conflicting files, explain each conflict, and resolve with the user's guidance.

## Stash

- Use `git stash push -m "<description>"` to name stashes meaningfully.
- Always list stash contents before applying or dropping.

## Log and inspection

- Use `git log --oneline --graph --decorate` for history overviews.
- Use `git show`, `git diff`, `git blame` for deep inspection.
- Use `git bisect` for tracking down regressions when asked.

## Tags and releases

- Use annotated tags (`git tag -a`) for releases with a meaningful message.
- Confirm before pushing tags to remote.

## Safety checklist before destructive operations

Before running any of: `reset --hard`, `push --force`, `branch -D`, `clean -f`, `checkout -- .`, `restore .`:
- State exactly what will be lost or overwritten.
- Confirm with the user.
- If operating on `main`/`master`, add an extra warning.

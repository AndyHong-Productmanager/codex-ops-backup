---
name: github
description: Inspect GitHub repositories, PRs, issues, reviews, and CI; publish authorized changes.
---

# GitHub

- Scope PR reads and review threads to their canonical base repository.
- For review fixes or writes, follow `../gh-address-comments/SKILL.md`.
- If Actions logs are unavailable, use
  `scripts/inspect_pr_checks.py --repo <matching-checkout> --pr <full-pr-url>`;
  report external checks and URLs for provider follow-up.

## Publish GitHub Changes

- Stage, commit, push, and PR creation each require explicit authorization;
  requesting one action never authorizes the others.
- Inspect staged and unstaged status/diffs; for mixed worktrees, ask which
  files belong. Stage only confirmed paths with `git add -- <paths>`; never
  stage unrelated changes. Never use `git add -A`, `git add .`, or
  `git add --all`.
- If on the default branch, create a feature branch before committing;
  otherwise preserve the requested or current branch. Push only when requested
  and only after confirming the staged scope.
- Resolve the exact base/head repositories and branches; reuse an existing
  matching PR instead of creating another.
- Create at most one PR. If creation is uncertain, verify read-only; never
  blindly retry.
- Set `draft: true`, unless explicitly requested `draft: false`.
- Supply exactly one `base`/`head` or `base_branch`/`head_branch` pair.
- Cross-repository heads, including same-organization `head_repo`, must use
  `<head-owner>:<branch>`.

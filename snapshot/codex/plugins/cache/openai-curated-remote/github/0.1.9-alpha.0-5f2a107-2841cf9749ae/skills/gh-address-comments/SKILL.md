---
name: gh-address-comments
description: Inspect GitHub PR review threads, implement local fixes, and perform authorized review actions.
---

# GitHub Review Threads

- Read authoritative review threads in the PR's base repository, not its fork
  or flat comments; check the current patch when a thread is outdated.
- If unavailable, use `scripts/fetch_comments.py` only for the exact
  current-branch base PR; otherwise use authenticated `gh api graphql`.
- Replies, reviews, and thread resolution each require explicit authorization;
  local fixes never authorize remote writes, commits, or pushes.
- Resolve only the approved thread's GraphQL thread ID, never a comment ID.

# Claim graph

## Verified claims

| claim_id | statement | claim type | risk tier | scope | intent ids | supporting observations | contradicting observations | independent observation groups | convergence status | counter-search result | primary source backing | dependencies | status | final synthesis location |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C-001 | No current public official OmO Desktop GUI installer was verified. | dated product-distribution | high | public distribution | I-001 | O-001, O-003, O-005; counter-search wave 3 | Internal Desktop references exist but no public installer URL. | Primary site/release and independent Korean/counter-search groups | supported; primary-only exception applies to distribution surfaces | Historical source 404; third-party candidates excluded | sitemap, documentation, and official release | O-001, O-003, O-005 | supported | SYNTHESIS.md |
| C-002 | `npx lazycodex-ai install` is the public official OmO-for-Codex installation path. | product-distribution | normal | Codex Desktop | I-001 | O-006 and official GitHub/LinkedIn announcement chain | None found | first-party repository and author announcement | supported | no stronger contrary source found | code-yeongyu/lazycodex | O-006 | supported | SYNTHESIS.md |
| C-003 | `npm i -g omo-ai@beta` is the official standalone OmO Native CLI install path, not a GUI installer. | product-distribution | normal | standalone CLI | I-001 | O-001, O-002, O-004 | None found | primary docs/registry and independent audit | supported | bare package and unrelated npm `omo` rejected | omo.dev and npm registry | O-001, O-002 | supported | SYNTHESIS.md |

| claim_id | statement | claim type | risk tier | scope | intent ids | supporting observations | contradicting observations | independent observation groups | convergence status | counter-search result | primary source backing | dependencies | status | final synthesis location |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C-001 | The returned OMO Desktop installation link is the current official channel. | dated product-distribution | high | OMO Desktop | I-001 | Pending first wave. | None known. | None yet. | pending | Pending. | Pending. | Canonical product identity. | unresolved | Pending. |

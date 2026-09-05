# Research quality review — REJECT

## Verdict

**REJECT (evidence-hygiene corrections required; the central no-GUI conclusion is not falsified).**

## Independent verification

- `https://omo.dev/docs` currently describes three editions: Codex **CLI** Light via `npx lazycodex-ai install`, and Senpi/native via `npm i -g omo-ai@beta`; it labels the latter a standalone beta. It does not publish a GUI Desktop installer.
- `https://github.com/code-yeongyu/oh-my-openagent/releases/latest` currently resolves to `https://github.com/code-yeongyu/oh-my-openagent/releases/tag/v5.0.0-beta.40`. Its assets are `omo-{platform}-{arch}` native executables plus `SHA256SUMS`, not a `.dmg`, `.pkg`, `.msi`, or AppImage GUI installer.
- `https://github.com/code-yeongyu/lazycodex` directly documents `npx lazycodex-ai install` as the OmO distribution for Codex. It is a Codex plugin distribution, not a separate OmO Desktop GUI installer.

Accordingly, the synthesis does **not** falsely claim that a public GUI Desktop installer exists. Its narrowly phrased conclusion—none was *verified* on the audited public first-party surfaces—is supported as of the review date. The historical URL `https://github.com/minpeter/omo-desktop-releases` currently returns 404, which supports unavailability only, not a universal non-existence claim.

## Findings

- **Citation accuracy: mostly pass.** Sources 1, 2, 3, and 5 support their stated installation/channel facts; the release and registry version (`5.0.0-0.beta.40`) agree at review. Source 6 is a 404 target, so it must be characterized as a dated failed-access observation rather than a normal evidentiary source. The exact historical AppImage URL is not listed, reducing reproducibility.
- **Scope discipline: needs correction.** The official docs call LazyCodex the Light edition for **Codex CLI**. `SYNTHESIS.md` says “For Codex Desktop”; this is an unsupported broadening and risks conflating Codex with the requested OmO Desktop GUI. It should say Codex CLI/plugin distribution and remain clearly separate from the unavailable GUI installer.
- **Source independence: qualified pass.** `omo.dev`, the official release, and LazyCodex are owner-controlled first-party surfaces, hence corroborative but not independent. That is appropriate for an official-distribution question. npm verifies published package metadata, while the independent `cmore.dev` audit only corroborates the CLI path and is not cited in the synthesis source list; it cannot prove GUI absence.
- **Blocking evidence hygiene:** `claim-graph.md` retains a second, unresolved C-001 asserting “The returned OMO Desktop installation link is the current official channel” with `Pending` status, directly conflicting with the supported C-001. `verification-economics.md` also ends C-001 as `pending`. These stale records make the research package internally inconsistent even though the synthesis conclusion is sound.

## Approval condition

Remove or clearly supersede the stale pending claim/verification entries, tighten “Codex Desktop” to “Codex CLI/plugin,” and record the historical 404 as a dated observation with the exact tested asset URL. Re-review is then expected to approve the research-only delivery.

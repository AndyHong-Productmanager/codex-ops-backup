# Manual QA — user-facing installation result

Checked 2026-09-04 (Asia/Seoul) against the four required live public routes. This is a read-only, user-facing-result check; no product files or research conclusions were changed.

| Check | Result | Live-page / HTTP observation | User-facing result verdict |
| --- | --- | --- | --- |
| 1. Codex installation link and command | **PASS** | `https://github.com/code-yeongyu/lazycodex` returned HTTP 200. Its Install section presents `npx lazycodex-ai install` as the one-line primary path, expands it to `npx --yes --package oh-my-openagent omo install --platform=codex`, and labels the marketplace alternative experimental. | The result links to this first-party repository and gives exactly `npx lazycodex-ai install`; this is supported as the OmO-for-Codex path. |
| 2. Native CLI link and command | **PASS** | `https://omo.dev/docs` returned HTTP 200. Installation identifies the Senpi Edition as a standalone beta and says `npm i -g omo-ai@beta`; it explicitly requires the `@beta` tag and distinguishes it from plugins. The current `https://github.com/code-yeongyu/oh-my-openagent/releases` page returned HTTP 200 and labels `v5.0.0-beta.40` Latest, with raw platform `omo-*` executable assets. | The result links to the official docs and gives `npm i -g omo-ai@beta`, accurately describing this as the standalone Native CLI channel. |
| 3. No misleading GUI-desktop claim | **PASS** | The official docs call the native edition a **standalone** command/edition, not a GUI application. The current release lists platform binary assets (for example `omo-darwin-arm64`, `omo-linux-x64`, and `omo-windows-arm64.exe`), not a `.dmg`, `.msi`, or AppImage GUI installer. | The result expressly says no current public first-party OmO Desktop GUI installer was verified and does not represent the Native CLI command as a GUI installer. Its Codex Desktop wording is scoped to using LazyCodex within the Codex desktop-app context. |
| 4. Historical/third-party desktop-link exclusion | **PASS** | `https://github.com/minpeter/omo-desktop-releases` returned HTTP 404; `https://api.github.com/repos/minpeter/omo-desktop-releases` also returned HTTP 404. The browser page could not render the repository and reported an internal-error response, consistent with the direct HTTP result. | The result warns readers not to use historical AppImage/third-party desktop candidates. It cites the `minpeter` URL only as negative evidence for the unavailable historical route, never as an installation recommendation. |

## Route status log

| Route | HTTP status | Exact observed behavior |
| --- | --- | --- |
| `https://github.com/code-yeongyu/lazycodex` | 200 | Install page renders `npx lazycodex-ai install`; primary npx path plus experimental Codex marketplace commands are visible. |
| `https://omo.dev/docs` | 200 | Installation table distinguishes Codex Light, OpenCode Ultimate, and standalone Senpi; Native command is `npm i -g omo-ai@beta`. |
| `https://github.com/code-yeongyu/oh-my-openagent/releases` | 200 | Latest release displayed as `v5.0.0-beta.40` (released 2026-09-04); release assets are named `omo-{platform}-{arch}` binaries with checksums. |
| `https://github.com/minpeter/omo-desktop-releases` | 404 | GitHub repository route is unavailable; matching GitHub API repository endpoint is also 404. |

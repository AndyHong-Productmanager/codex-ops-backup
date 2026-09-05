# ULW-Research Synthesis: OMO Desktop installation link

Workers: 6 · Waves: 3 · Excursions: 0 · Sources: 13 (9 domains) · Verifications: 4 · Elapsed: 14 min

## Executive summary

No current public first-party OmO Desktop GUI installer was verified. The former Desktop AppImage source is unavailable. The reliable, publicly documented paths are OmO for Codex through LazyCodex and the standalone OmO Native CLI through `omo-ai@beta`.

For Codex Desktop, use `npx lazycodex-ai install` from the first-party LazyCodex distribution. For standalone OmO Native, use `npm i -g omo-ai@beta`; the `@beta` tag is mandatory. Do not use npm package `omo`, historical AppImage links, AUR `omo-desktop-bin`, or third-party desktop mirrors as an official Desktop installer.

## Findings by theme

### OmO for Codex/Desktop

Kim Yeongyu's first-party distribution is [LazyCodex](https://github.com/code-yeongyu/lazycodex), which supports OmO in Codex including the desktop app context. The official installation command is `npx lazycodex-ai install`. [Source 1]

### Standalone OmO Native CLI

The official documentation calls the Senpi edition a standalone beta and prescribes `npm i -g omo-ai@beta`, followed by `omo`. Registry metadata confirms current beta `5.0.0-0.beta.40`; the package exposes a JavaScript `omo` bin and needs Node >=24. [Source 2] [Source 3]

### Separate GUI Desktop installer

The official site sitemap, current GitHub release, and first-party docs do not expose a Desktop GUI download. The historical v0.0.33 AppImage source is now 404. Current release assets are CLI binaries, not GUI installers. [Source 4] [Source 5] [Source 6]

## Verified claims

- C-001 (supported): No current public official OmO Desktop GUI installer was verified as of 2026-09-04. Primary-only exception: first-party sitemap, docs, and release assets are the authoritative distribution surfaces.
- C-002 (supported): `npx lazycodex-ai install` is the official OmO-for-Codex distribution command.
- C-003 (supported): `npm i -g omo-ai@beta` is the official standalone OmO Native CLI command; it is not a GUI Desktop installer.

## Contradictions

Recent first-party references to “OmO Desktop” and internal RPC compatibility demonstrate a host exists, but none provides a public installer. This differs from public CLI/Codex availability; the two must not be conflated.

## Gaps

Private, invite-only, or future Desktop distribution cannot be disproven. No publicly installable first-party GUI link was present in the audited sources.

## Sources

1. https://github.com/code-yeongyu/lazycodex
2. https://omo.dev/docs
3. https://registry.npmjs.org/omo-ai
4. https://omo.dev/sitemap.xml
5. https://github.com/code-yeongyu/oh-my-openagent/releases/tag/v5.0.0-beta.40
6. https://github.com/minpeter/omo-desktop-releases


# Wave 1: source territories

## Canonical site

The primary-site observer opened `https://omo.dev/` and its installation documentation at 2026-09-04T17:15:50+09:00. The official standalone channel is `npm i -g omo-ai@beta` followed by `omo`; the site calls it the Senpi Edition, a standalone beta, and does not provide a public GUI installer page. Evidence: `.omo/teams/team-da9e3128/artifacts/primary-site.md`.

## npm registry

The npm-channel observer directly checked the registry. `omo-ai@beta` resolves to `5.0.0-0.beta.40`, published 2026-09-04T04:00:21.607Z, with a `omo` JavaScript bin and Node >=24. It is a CLI distribution, not a `.dmg`, `.exe`, `.msi`, or AppImage installer. Sources: `https://registry.npmjs.org/omo-ai`, `https://www.npmjs.com/package/omo-ai`.

## GitHub release assets

The GitHub-releases observer found `code-yeongyu/oh-my-openagent` release `v5.0.0-beta.40`, whose native CLI assets include platform binaries and SHA256SUMS. It reported no public code-yeongyu desktop repository or GUI release asset. One Linux binary was hash-checked and reported its version as `omo 5.0.0-0.beta.40 (engine: senpi 2026.9.4)`.

## Independent and counter evidence

Korean coverage and an independent audit corroborate the public Native CLI channel, not a desktop installer. Counter-search found similarly named third-party desktop ports/mirrors that explicitly state they are unofficial; they must not be presented as an official installation source.

## EXPAND markers

- LEAD: Locate a first-party signed OmO Desktop installer released after 2026-09-01 — WHY: first-wave primary and independent sources distinguish Desktop from the public Native CLI — ANGLE: direct official site/GitHub release artifact audit.
- DEAD END: Generic OMO Desktop download searches return unrelated software or untrusted third-party ports.


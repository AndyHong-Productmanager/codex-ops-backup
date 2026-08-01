---
slug: discord-bot-reliability
status: drafting
intent: clear
review_required: false
pending-action: resolve owner decisions, then write .omo/plans/discord-bot-reliability.md
approach: one singleton Discord ingress with durable per-session scheduling, explicit adapter outcomes, backend-specific readiness, and systemd-owned CLI process trees
---

# Draft: discord-bot-reliability

## Components (topology ledger)
<!-- Lock the SHAPE before depth. One row per top-level component that can succeed or fail independently. -->
<!-- id | outcome (one line) | status: active|deferred | evidence path -->
| discord-ingress | Exactly one Discord Gateway client accepts and routes each message once. | active | `/home/ubuntuhong/dev/claude-discord-bot/multi_bot.py:278`, `/home/ubuntuhong/dev/claude-discord-bot/claude_discord_bot.py:319`; both currently run. |
| scheduler-session-store | A durable, canonical per-session queue prevents overlapping work and duplicate delivery. | active | `/home/ubuntuhong/dev/claude-discord-bot/multi_bot.py:278-405`; other bots use incompatible global/session files. |
| backend-adapters-readiness | Each backend returns typed, non-empty success or explicit failure without blocking healthy routes. | active | Kimi `:311-343`, OpenCode `:338-457`, Qwen `:273-353`, Senpi `:315-406`, Claude `:180-274`. |
| cli-process-control | CLI work owns every descendant process and timeout cleanup through a transient systemd scope. | active | `/home/ubuntuhong/dev/senpi-discord-bot/senpi_discord_bot.py:315-383`; runtime cgroup has Chromium and CodeGraph descendants. |
| cutover-and-recovery | Legacy consumers are removed only after explicit readiness, recovery, cancellation, and rollback verification. | active | Active user services and recent failures captured by `systemctl --user` and `journalctl --user` on 2026-07-30. |

## Open assumptions (announced defaults)
<!-- Record any default you adopt instead of asking, so the user can veto it at the gate. -->
<!-- assumption | adopted default | rationale | reversible? -->
| Test harness | Add local `unittest.IsolatedAsyncioTestCase` coverage; no existing test runner/configuration exists. | Every target is Python and no test infrastructure was found. | yes |
| Backend protocol migration | Keep existing Kimi/OpenCode/Qwen HTTP/WS protocols behind adapters in the first cutover. | Removing daemons and rewriting all providers at once is an unnecessary outage risk. | yes |
| Readiness isolation | A degraded backend rejects only its own route; healthy routes continue. | Existing backends fail independently. | yes |
| Admin restart authority | Discord user commands must not invoke `systemctl`; backend restarts belong to the supervisor/admin path. | Prevents a chat request from mutating host service state. | yes |
| Empty-output rule | Never render a successful empty response; classify it as `EMPTY_OUTPUT` with a correlation ID. | Existing short-text heuristics and user strings obscure failure state. | yes |

## Findings (cited - path:lines)

- `senpi-discord-bot.service` currently owns Chromium/Puppeteer and CodeGraph descendants: 91 tasks, about 985 MiB current and 2.47 GiB peak. The code only applies `os.killpg()` to the launcher process group at timeout: `/home/ubuntuhong/dev/senpi-discord-bot/senpi_discord_bot.py:339-359`.
- Kimi, OpenCode, and Qwen actively route work through persistent daemons. Their active units expose ports 58627, 4180, and 4170 respectively. Kimi performs REST+WebSocket work at `/home/ubuntuhong/dev/kimi-discord-bot/kimi_discord_bot.py:477-579`; OpenCode uses `/session` HTTP endpoints at `/home/ubuntuhong/dev/opencode-discord-bot/opencode_discord_bot.py:258-429`; Qwen posts and polls daemon state at `/home/ubuntuhong/dev/qwen-discord-bot/qwen_discord_bot.py:406-502`.
- OpenCode readiness accepts any positive HTTP status, including a server error: `/home/ubuntuhong/dev/opencode-discord-bot/opencode_discord_bot.py:338-344`.
- Qwen client timeouts bypass parts of its recovery path because `asyncio.TimeoutError` is not caught alongside `aiohttp.ClientError`: `/home/ubuntuhong/dev/qwen-discord-bot/qwen_discord_bot.py:406-502`.
- Claude has two active independently cgrouped Gateway clients. Both read `DISCORD_BOT_TOKEN` from `/home/ubuntuhong/dev/claude-discord-bot/.env`: `/home/ubuntuhong/dev/claude-discord-bot/multi_bot.py:43,132,610` and `/home/ubuntuhong/dev/claude-discord-bot/claude_discord_bot.py:58,88,425`.
- Existing replies mix strings, sentinel empty-output messages, and exceptions. Claude can return parsed output despite a nonzero process exit: `/home/ubuntuhong/dev/claude-discord-bot/claude_discord_bot.py:180-224`.
- No test configuration or tests were present in the five target bot directories. The critical red-test seams are Senpi timeout cleanup and all final Discord delivery paths.
- Local systemd is v255 with cgroup v2. `systemd-run --user --scope` can create a per-request sibling scope in `app.slice`; `KillMode=control-group`, `RuntimeMaxSec`, `BindsTo`, `After`, and `--collect` provide descendant cleanup without unsupported direct cgroup manipulation.

## Decisions (with rationale)

- Use a single Discord ingress process as the only owner of its selected token. It persists a job keyed by Discord message ID before dispatch, then delegates to adapters instead of running backend work in the event callback.
- Introduce an `Outcome` result contract rather than user-visible strings: non-empty success, empty output, timeout with known/unknown commit, unavailable backend, process exit with code, rejected, and cancelled. The ingress renders stable Korean responses with a correlation ID and never treats empty output as success.
- Make session state canonical and durable, with FIFO single-worker scheduling per session key. Backends retain their current transport during the first migration but receive the canonical scope and idempotency key.
- Start CLI jobs through named transient systemd scopes and cancel them with `systemctl --user stop <scope>`, never by killing the `systemd-run` wrapper or only its process group.
- Gate each route on its own semantic readiness; service-active/Discord-ready is not end-to-end ready.
- Cut over only in a maintenance window, with legacy units and session files preserved for rollback. Never replay an interrupted running job without backend reconciliation.

## Scope IN

- The currently active Claude, Kimi, OpenCode, Qwen, and Senpi Discord paths.
- One ingress, per-route readiness, durable session/job state, queue/backpressure, explicit outcomes, safe subprocess lifecycle, and service cutover/rollback steps.
- Failing-first unit/integration-style tests with fake Discord/backend/process boundaries and one controlled live service QA cycle.

## Scope OUT (Must NOT have)

- No edits under `orchestra/`, `docs/rag/`, or `docs/obsidian/`.
- No blind replay of interrupted jobs, deletion of legacy session data, or overlapping legacy/singleton Gateway consumers during cutover.
- No provider protocol rewrite in the initial migration and no Discord command that restarts a host service.

## Open questions

1. Sole ingress identity: which existing Discord bot token/identity should own the unified Gateway? Recommended: the current `claude-discord-bot` identity after its duplicate direct router is stopped.
2. Conversation isolation: should a session be `backend:guild:channel:user` (recommended), per-channel shared, or intentionally shared per backend? This changes state migration and tool isolation.
3. Execution semantics after a timeout whose backend may already have changed files/tools: at-most-once with an explicit `UNKNOWN` outcome (recommended), or automatic retry? This is an irreversible behavior contract.
4. Queue policy: confirm a default capacity of 10 jobs per canonical session with 24-hour terminal-job retention, or provide different limits. This becomes a user-facing backpressure/data-retention policy.
5. Scope confirmation: include exactly the five active bots and leave inactive Qoder out (recommended), or include Qoder in the migration too?

## Approval gate
status: awaiting-approval
<!-- When exploration is exhausted and unknowns are answered, set status: awaiting-approval. -->
<!-- That durable record is the loop guard: on a later turn read it and resume at the gate instead of re-running exploration. -->
Approach: build one selected-token ingress and move the five active backend paths behind durable scheduling, per-route semantic readiness, typed non-empty outcomes, and systemd-owned CLI scopes. Preserve current daemon protocols initially; cut over only after tests and controlled live QA prove readiness, timeout, cancellation, delivery, restart recovery, and rollback.
Next workflow action: after Andy confirms the five owner decisions above (or accepts the recommended defaults), generate `.omo/plans/discord-bot-reliability.md`; implementation then starts in a separate worker session via `$start-work discord-bot-reliability`.

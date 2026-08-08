# Standalone Codex Telegram Bot

Independent Telegram router for Codex. It does not import or call `orchestra` scripts.

## Run

```bash
cd /home/ubuntuhong/dev/codex-telegram-bot
nohup python3 telegram_codex_bot.py > logs/router.stdout.log 2>&1 &
```

## Healthcheck

`healthcheck.sh` verifies that the router PID belongs to this workspace and
that its polling loop heartbeat is no more than 180 seconds old. It stops and
replaces an unresponsive router automatically. Run it once with:

```bash
./healthcheck.sh
```

For automatic recovery, register this cron entry (every minute):

```cron
* * * * * /home/ubuntuhong/dev/codex-telegram-bot/healthcheck.sh >> /home/ubuntuhong/dev/codex-telegram-bot/logs/healthcheck.cron.log 2>&1
```

Set `HEALTHCHECK_HEARTBEAT_MAX_AGE_SECONDS` to change the 180-second timeout.

## State

- `.env`: copied Telegram bot token and chat id
- `var/telegram.offset`: Telegram update offset
- `var/codex.session`: rolling Codex session UUID
- `var/healthcheck.status`: last observed router state
- `var/router.heartbeat`: most recent completed router polling-loop iteration
- `logs/router.log`: runtime log
- `logs/healthcheck.log`: healthcheck state changes and recovery attempts

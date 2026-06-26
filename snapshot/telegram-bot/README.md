# Standalone Codex Telegram Bot

Independent Telegram router for Codex. It does not import or call `orchestra` scripts.

## Run

```bash
cd /home/ubuntuhong/dev/codex-telegram-bot
nohup python3 telegram_codex_bot.py > logs/router.stdout.log 2>&1 &
```

## State

- `.env`: copied Telegram bot token and chat id
- `var/telegram.offset`: Telegram update offset
- `var/codex.session`: rolling Codex session UUID
- `logs/router.log`: runtime log


# Codex Ops Backup

Private backup repository for the local Codex operating setup.

It captures:

- Codex config shape and trusted project/plugin settings
- local Codex skills
- plugin skill bundles and lightweight plugin metadata
- LazyCodex/omo skill metadata
- standalone Telegram router source
- install scripts for restoring the same structure on another server

It deliberately does not capture:

- Telegram bot token or chat id
- runtime logs
- Codex sessions
- generated images
- plugin runtime caches and binaries

## Manual Backup

```bash
/home/ubuntuhong/dev/codex-ops-backup/scripts/backup.sh
```

## Install On Another Server

```bash
git clone git@github.com:AndyHong-Productmanager/codex-ops-backup.git
cd codex-ops-backup
./scripts/install.sh
```

After install, create `/home/$USER/dev/codex-telegram-bot/.env` with:

```bash
TG_CODEX_BOT_TOKEN=
TG_CHAT_ID=
```

Then start the router:

```bash
cd /home/$USER/dev/codex-telegram-bot
nohup python3 telegram_codex_bot.py > logs/router.stdout.log 2>&1 &
```

## Cron

This server uses `scripts/install-cron.sh` to register a weekly Sunday backup job.

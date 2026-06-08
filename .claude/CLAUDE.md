# CLAUDE.md

This file guides Claude Code when working in this repository.

## Overview

**NoDuplicates** (Discord Media Repost Detector) is a Discord bot that detects
when a YouTube video or Instagram Reel link has already been shared **anywhere in
a server** (cross-channel, within a guild). When a duplicate is found, it replies
to the new message with a (humorous, Traditional Chinese) notice and a jump link
to the original post.

Detection is backed by a persistent per-guild **SQLite index** that is warmed once
on startup and kept current live — so the hot path is an O(1) index lookup, not a
Discord history scan. Each guild has its own **JSON config**, edited via admin
slash commands.

## Architecture

A single bot process (`python main.py`). Modules:

- **`main.py`** — entry point. Builds a `commands.Bot` (Message Content Intent on),
  opens the DB, loads the cogs, and syncs the app-command tree in `setup_hook`.
  Loads `TOKEN` from `.env`.
- **`media.py`** — URL parsing. `extract_media_id(url)` → `(type, id)`:
  - `"yt"` — `youtube.com/watch?v=`, `/shorts/`, `/live/`, `youtu.be/`.
  - `"ig"` — `/reel/`, `/reels/`.
  - `extract_all(content)` returns de-duplicated `(type, id)` pairs from a message.
  - `platform_name(type)` maps to a display name. Add new platforms here.
- **`db.py`** — SQLite layer (`data/index.db`). Single `media` table with PK
  `(guild_id, media_type, media_id)`, so `record()` uses `INSERT OR IGNORE` and
  **the first poster is always kept as the original**. `find()` is a PK lookup;
  `prune(guild_id, ttl_days)` drops expired rows; `remove_message()` clears a row
  when its source message is deleted; `count()` for status.
- **`config.py`** — per-guild JSON at `data/guilds/{guild_id}.json`. `load()` merges
  saved values over `DEFAULTS` (forward-compatible); `save()` writes atomically.
  Keys: `enabled`, `whitelist_channels` (empty = all channels), `ttl_days`,
  `reply_template` (`{platform}`, `{author}`, `{link}`).
- **`cogs/detector.py`** — the `on_message` listener (lookup → reply or record),
  startup backfill of watched channels within the TTL window (`on_ready`, capped at
  `BACKFILL_LIMIT`), the hourly `prune_loop`, and `on_raw_message_delete` cleanup.
- **`cogs/admin.py`** — `/repost` slash-command group (gated by `manage_guild`):
  `enable`/`disable`, `ttl`, `status`, `channel add|remove|list`,
  `message set|reset`.

Detection is always **guild-wide** (across channels); there is intentionally no
per-channel-only mode, because the per-guild PK can't represent it correctly.
Servers never match against each other.

## Running locally

```bash
pip install -r requirements.txt
# create .env with TOKEN=your_discord_bot_token
python main.py
```

The bot requires the **Message Content Intent** (set in code via
`intents.message_content = True`; must also be enabled in the Discord Developer
Portal). On first run it syncs slash commands and backfills recent history.

## Deployment

Runs as a plain long-lived worker (e.g. `python main.py` under systemd / a
container / any always-on host). It no longer needs an open HTTP port, so free web
hosts that require one are not suitable. The `data/` directory (SQLite DB + guild
configs) must persist across restarts and is gitignored.

## Conventions & notes

- **No code comments**: do not add explanatory comments to code in this repo.
- **Secrets**: `TOKEN` lives only in `.env` (gitignored). Never commit it.
- **Runtime state**: everything under `data/` is gitignored; never commit it.
- User-facing bot messages are in Traditional Chinese — keep that tone if editing them.
- Python 3.10+ is required (the code uses `tuple[str, str] | None` syntax).
- There is no test suite or linter configured.
- Startup backfill is bounded (`BACKFILL_LIMIT` in `cogs/detector.py`); the
  persistent index means deep history scans don't repeat on the hot path.

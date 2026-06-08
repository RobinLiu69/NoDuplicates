import json
import os
import tempfile
from pathlib import Path

GUILDS_DIR = Path(__file__).parent / "data" / "guilds"

DEFAULTS = {
    "enabled": True,
    "whitelist_channels": [],
    "ttl_days": 30,
    "reply_template": (
        "搞笑囉 這支 {platform} 之前就被 {author} 傳過囉！\n"
        "原訊息連結：{link}\n"
        "再不讀訊息阿"
    ),
}


def _path(guild_id) -> Path:
    return GUILDS_DIR / f"{guild_id}.json"


def load(guild_id) -> dict:
    cfg = dict(DEFAULTS)
    path = _path(guild_id)
    if path.exists():
        try:
            cfg.update(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            pass
    return cfg


def save(guild_id, cfg) -> None:
    GUILDS_DIR.mkdir(parents=True, exist_ok=True)
    path = _path(guild_id)
    fd, tmp = tempfile.mkstemp(dir=GUILDS_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

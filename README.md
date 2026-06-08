# Discord Media Repost Detector

This project is a Discord bot that prevents redundant content sharing by tracking YouTube and Instagram Reel URLs **across all channels of a server**. It automatically identifies duplicate media submissions and references the original post.

[English Version](#English-Version) | [中文版本](#中文版本)

---

## English Version

### Project Overview

The Media Repost Detector maintains a persistent **per-server media index** (SQLite). Every YouTube / Instagram Reel link is reduced to a unique media ID and stored on first sight. When the same link is posted again — in any channel of the same server — the bot replies with a jump link to the original message. Detection is an O(1) index lookup, not a history scan, so it stays fast as the server grows.

### Key Features

* **Cross-channel detection**: a link reposted in any channel of the server is caught, not just the channel it was first posted in.
* **Persistent index**: SQLite-backed, warmed once on startup and kept current live; survives restarts.
* **Time-based expiry (TTL)**: because tracked content is short-lived, old entries are pruned automatically (configurable per server).
* **Per-server configuration**: each server has its own settings, managed through admin slash commands.
* **Media ID extraction**: robust parsing for YouTube (Standard, Shorts, Live) and Instagram Reels.

### Slash Commands

All commands are under `/repost` and require the **Manage Server** permission.

| Command | Description |
| --- | --- |
| `/repost enable` / `/repost disable` | Turn detection on/off for the server |
| `/repost status` | Show current settings and index size |
| `/repost ttl <days>` | Set how long entries are kept |
| `/repost channel add\|remove\|list` | Manage the channel whitelist (empty = all channels) |
| `/repost message set <template>` | Customize the reply (`{platform}`, `{author}`, `{link}`) |
| `/repost message reset` | Restore the default reply message |

### Technical Specifications

* **Language**: Python 3.10+
* **Libraries**: `discord.py` (native slash-command support), `python-dotenv`
* **Storage**: SQLite (media index) + JSON (per-server config), under `data/`

### Installation and Configuration

1. **Clone the repository**
```bash
git clone <repository_url>
cd <repository_directory>
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment setup** — create a `.env` file in the root directory:
```env
TOKEN=your_discord_bot_token
```

4. **Enable the Message Content Intent** for the bot in the Discord Developer Portal.

5. **Run**
```bash
python main.py
```
On first run the bot syncs its slash commands and backfills recent history.

### Deployment

Run it as a long-lived worker process (systemd, a container, or any always-on host). The bot does **not** open an HTTP port, so free web hosts that require one are not suitable. The `data/` directory holds the SQLite index and per-server configs — it must persist across restarts and is gitignored.

---

## 中文版本

### 專案簡介

本專案為一款 Discord 機器人，透過維護**每個伺服器專屬的媒體索引**（SQLite），防止重複內容分享。每個 YouTube / Instagram Reel 連結會被轉成唯一的媒體 ID 並在第一次出現時記錄。當同一連結再次被張貼——無論在伺服器的哪個頻道——機器人都會回覆原始訊息的跳轉連結。偵測為 O(1) 索引查詢，不需掃描歷史訊息，伺服器再大也維持快速。

### 主要功能

* **跨頻道偵測**：連結在伺服器任一頻道重貼都會被抓到，不限於原始頻道。
* **持久化索引**：以 SQLite 儲存，啟動時暖機一次並即時更新，重啟後仍保留。
* **時間到期（TTL）**：因追蹤內容多為短期，過舊的紀錄會自動清除（每個伺服器可調整）。
* **每伺服器獨立設定**：每個伺服器擁有自己的設定，透過管理員斜線指令管理。
* **媒體 ID 提取**：精準解析 YouTube（一般影片、Shorts、直播）與 Instagram Reels。

### 斜線指令

所有指令皆在 `/repost` 之下，需具備**管理伺服器**權限。

| 指令 | 說明 |
| --- | --- |
| `/repost enable`／`/repost disable` | 開啟／關閉偵測 |
| `/repost status` | 顯示目前設定與索引筆數 |
| `/repost ttl <天數>` | 設定紀錄保留天數 |
| `/repost channel add\|remove\|list` | 管理頻道白名單（空白＝全部頻道） |
| `/repost message set <模板>` | 自訂回覆訊息（`{platform}`、`{author}`、`{link}`） |
| `/repost message reset` | 還原預設回覆訊息 |

### 技術規格

* **開發語言**：Python 3.10+
* **主要套件**：`discord.py`（內建斜線指令）、`python-dotenv`
* **資料儲存**：SQLite（媒體索引）＋ JSON（每伺服器設定），存於 `data/`

### 安裝與設定流程

1. **複製儲存庫**
```bash
git clone <repository_url>
cd <repository_directory>
```

2. **安裝必要套件**
```bash
pip install -r requirements.txt
```

3. **環境變數設定** — 於根目錄建立 `.env`：
```env
TOKEN=您的Discord機器人Token
```

4. **於 Discord Developer Portal 啟用機器人的 Message Content Intent。**

5. **啟動**
```bash
python main.py
```
首次啟動時，機器人會同步斜線指令並回填近期歷史訊息。

### 部署說明

以長駐的工作程序執行（systemd、容器，或任何持續在線的主機）。機器人**不會**開啟 HTTP 連接埠，因此需要開放連接埠的免費網頁主機並不適用。`data/` 目錄存放 SQLite 索引與各伺服器設定，必須在重啟後保留，且已列入 gitignore。

# Discord Media Repost Detector

This project is a Discord bot designed to prevent redundant content sharing by monitoring YouTube and Instagram Reel URLs within channels. It automatically identifies duplicate media submissions and references the original post.

[English Version](#English-Version) | [中文版本](#中文版本)

---

## English Version

### Project Overview

The Media Repost Detector scans incoming messages for specific media URLs. By extracting unique media identifiers (IDs), it compares new posts against the channel's history. If a duplicate is found within the last 1000 messages, the bot notifies the user and provides a jump link to the original occurrence.

### Key Features

* **Media ID Extraction**: Robust parsing for YouTube (Standard, Shorts, Live) and Instagram Reels.
* **History Analysis**: Efficiently scans the previous 1000 messages for content matching.
* **Contextual Referencing**: Generates Discord jump URLs to direct users to the original message.
* **Uptime Support**: Integrated Flask server for compatibility with hosting platforms requiring an active HTTP port (e.g., Render).

### Technical Specifications

* **Language**: Python 3.10+
* **Primary Libraries**: `discord.py`, `Flask`, `python-dotenv`
* **Web Server**: `Gunicorn` (for production deployment)

### Installation and Configuration

1. **Clone the Repository**
```bash
git clone <repository_url>
cd <repository_directory>

```


2. **Install Dependencies**
```bash
pip install -r requirements.txt

```


3. **Environment Setup**
Create a `.env` file in the root directory:
```env
TOKEN=your_discord_bot_token

```


4. **Local Execution**
```bash
python main.py

```



### Deployment (Render)

* **Build Command**: `pip install -r requirements.txt`
* **Start Command**: `gunicorn server:app & python main.py`

---

## 中文版本

### 專案簡介

本專案為一款 Discord 機器人，旨在透過監測頻道內的 YouTube 與 Instagram Reel 連結，防止重複內容分享。系統會自動識別重複的媒體投稿，並引導使用者參考原始訊息。

### 主要功能

* **媒體 ID 提取**：精準解析 YouTube（一般影片、Shorts、直播）與 Instagram Reels 的唯一識別碼。
* **歷史紀錄分析**：自動檢索頻道內最近 1000 則訊息進行比對。
* **原始訊息引用**：自動生成跳轉連結，協助使用者快速定位首次分享的紀錄。
* **在線維持機制**：內建 Flask 伺服器，確保機器人符合雲端平台（如 Render）的運行需求。

### 技術規格

* **開發語言**：Python 3.10+
* **主要套件**：`discord.py`, `Flask`, `python-dotenv`
* **生產伺服器**：`Gunicorn`

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


3. **環境變數設定**
於根目錄建立 `.env` 檔案並配置 Token：
```env
TOKEN=您的Discord機器人Token

```


4. **本機啟動**
```bash
python main.py

```



### 部署說明 (以 Render 為例)

* **構建指令 (Build Command)**：`pip install -r requirements.txt`
* **啟動指令 (Start Command)**：`gunicorn server:app & python main.py`

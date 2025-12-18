import discord, re, os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

load_dotenv()
TOKEN = os.getenv("TOKEN")

URL_PATTERN = re.compile(r'https?://\S+')

def extract_media_id(url: str) -> tuple[str, str] | None:
    """
    Returns (type, unique_id). Example: ('yt', 'dQw4w9WgXcQ') or ('ig', 'DR6ul_8j71E')
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "").lower()
        path = parsed.path

        if "youtube.com" in domain:
            if path.startswith("/watch"):
                return "yt", parse_qs(parsed.query).get("v", [None])[0]
            if path.startswith(("/shorts/", "/live/")):
                return "yt", path.split("/")[2]
        elif "youtu.be" in domain:
            return "yt", path.lstrip("/")

        if "instagram.com" in domain:
            if "/reels/" in path or "/reel/" in path:
                parts = path.split("/")
                idx = parts.index("reels") if "reels" in parts else parts.index("reel")
                if len(parts) > idx + 1:
                    return "ig", parts[idx + 1]
    except Exception:
        pass
    return None

class BotClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        urls = URL_PATTERN.findall(message.content)
        if not urls:
            return

        for url in urls:
            media_info = extract_media_id(url)
            if not media_info:
                continue
            
            media_type, media_id = media_info
            
            skip = False
            async for old_msg in message.channel.history(limit=1000, before=message):
                if old_msg.author.bot:
                    skip = True
                    continue
                elif skip == True:
                    skip = False
                    continue
                
                old_urls = URL_PATTERN.findall(old_msg.content)
                for old_url in old_urls:
                    old_info = extract_media_id(old_url)
                    
                    if old_info and old_info == (media_type, media_id):
                        author_name = old_msg.author.display_name
                        
                        prefix = "YouTube" if media_type == "yt" else "Instagram Reel"
                        await message.reply(
                            f"搞笑囉 這支 {prefix} 之前就被 {author_name} 傳過囉！\n"
                            f"原訊息連結：{old_msg.jump_url}\n"
                            f"再不讀訊息阿",
                            suppress_embeds=True
                        )
                        return

intents = discord.Intents.default()
intents.message_content = True
client = BotClient(intents=intents)

if TOKEN:
    client.run(TOKEN)
else:
    print("TOKEN invalid.")
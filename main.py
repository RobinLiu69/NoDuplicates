import discord, re, os
from discord.ext import commands
from urllib.parse import urlparse, parse_qs

def extract_youtube_id(url: str) -> str | None:
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "").lower()

    if "youtube.com" in domain:
        if parsed.path.startswith("/watch"):
            query = parse_qs(parsed.query)
            return query.get("v", [None])[0]
        elif parsed.path.startswith("/shorts/"):
            return parsed.path.split("/shorts/")[1].split("/")[0]
    elif "youtu.be" in domain:
        return parsed.path.lstrip("/").split("/")[0]
    return None

def is_same_youtube_video(url1: str, url2: str) -> bool:
    id1 = extract_youtube_id(url1)
    id2 = extract_youtube_id(url2)
    return id1 is not None and id1 == id2

def normalize_youtube_url(url: str) -> str:
    vid = extract_youtube_id(url)
    return f"https://youtube.com/watch?v={vid}" if vid else url


class BotClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        if message.author == self.user:
            return

        
        urls = re.findall(r'https?://\S+', message.content)
        print(urls)
        if not urls:
            return
        
        yt_urls = [u for u in urls if "youtu" in u]
        if not yt_urls:
            return
        
        for url in yt_urls:
            normalized = normalize_youtube_url(url)
            video_id = extract_youtube_id(url)

            if not video_id:
                continue

            async for old_msg in message.channel.history(limit=1000, before=message):
                if old_msg.author == self.user:
                    continue
                for old_url in re.findall(r'https?://\S+', old_msg.content):
                    if extract_youtube_id(old_url) == video_id:
                        jump_url = old_msg.jump_url
                        author_name = (
                            old_msg.author.display_name
                            if hasattr(old_msg.author, "display_name")
                            else old_msg.author.name
                        )
                        await message.reply(
                            f"搞笑囉 這支影片之找就被 {author_name} 傳過囉！\n"
                            f"原訊息連結：{jump_url}\n"
                            f"影片：{normalize_youtube_url(old_url)}"
                            f"再不讀訊息阿",
                            suppress_embeds=True
                        )
                        return

        await self.process_commands(message)
        

token = os.getenv("TOKEN")
                
intents = discord.Intents.default()
intents.message_content = True
client = BotClient(intents=intents)
client.run(token)

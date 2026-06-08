import datetime

import discord
from discord.ext import commands, tasks

import config
import db
import media

BACKFILL_LIMIT = 1000


class Detector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._backfilled = False

    async def cog_load(self):
        self.prune_loop.start()

    async def cog_unload(self):
        self.prune_loop.cancel()

    def _watched_channels(self, guild, cfg):
        whitelist = cfg.get("whitelist_channels") or []
        for channel in guild.text_channels:
            if whitelist and channel.id not in whitelist:
                continue
            perms = channel.permissions_for(guild.me)
            if perms.read_message_history and perms.read_messages:
                yield channel

    @commands.Cog.listener()
    async def on_ready(self):
        if self._backfilled:
            return
        self._backfilled = True
        for guild in self.bot.guilds:
            await self._backfill_guild(guild)
        print("Backfill complete.")

    async def _backfill_guild(self, guild):
        cfg = config.load(guild.id)
        if not cfg.get("enabled", True):
            return
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            days=cfg.get("ttl_days", 30)
        )
        for channel in self._watched_channels(guild, cfg):
            try:
                async for msg in channel.history(
                    limit=BACKFILL_LIMIT, after=cutoff, oldest_first=True
                ):
                    if msg.author.bot:
                        continue
                    self._record_message(msg)
            except (discord.Forbidden, discord.HTTPException):
                continue

    def _record_message(self, message):
        for media_type, media_id in media.extract_all(message.content):
            db.record(
                message.guild.id,
                media_type,
                media_id,
                message.channel.id,
                message.id,
                message.author.id,
                message.author.display_name,
                message.jump_url,
                int(message.created_at.timestamp()),
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return

        cfg = config.load(message.guild.id)
        if not cfg.get("enabled", True):
            return

        whitelist = cfg.get("whitelist_channels") or []
        if whitelist and message.channel.id not in whitelist:
            return

        found = media.extract_all(message.content)
        if not found:
            return

        for media_type, media_id in found:
            hit = db.find(message.guild.id, media_type, media_id)
            if hit and hit["message_id"] != message.id:
                await self._reply_duplicate(message, cfg, media_type, hit)
                return
            if not hit:
                db.record(
                    message.guild.id,
                    media_type,
                    media_id,
                    message.channel.id,
                    message.id,
                    message.author.id,
                    message.author.display_name,
                    message.jump_url,
                    int(message.created_at.timestamp()),
                )

    async def _reply_duplicate(self, message, cfg, media_type, hit):
        text = cfg.get("reply_template", config.DEFAULTS["reply_template"]).format(
            platform=media.platform_name(media_type),
            author=hit["author_name"],
            link=hit["jump_url"],
        )
        if hit["channel_id"] != message.channel.id:
            text += f"\n（原本發在 <#{hit['channel_id']}>）"
        try:
            await message.reply(text, suppress_embeds=True)
        except (discord.Forbidden, discord.HTTPException):
            pass

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if payload.guild_id:
            db.remove_message(payload.guild_id, payload.message_id)

    @tasks.loop(hours=1)
    async def prune_loop(self):
        for guild in self.bot.guilds:
            cfg = config.load(guild.id)
            db.prune(guild.id, cfg.get("ttl_days", 30))

    @prune_loop.before_loop
    async def before_prune(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Detector(bot))

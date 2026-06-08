import discord
from discord import app_commands
from discord.ext import commands

import config
import db


class Admin(commands.Cog):
    repost = app_commands.Group(
        name="repost",
        description="重複貼文偵測設定",
        default_permissions=discord.Permissions(manage_guild=True),
        guild_only=True,
    )
    channel = app_commands.Group(
        name="channel", description="白名單頻道設定", parent=repost
    )
    message = app_commands.Group(
        name="message", description="回覆訊息設定", parent=repost
    )

    def __init__(self, bot):
        self.bot = bot

    @repost.command(name="enable", description="啟用偵測")
    async def enable(self, interaction: discord.Interaction):
        cfg = config.load(interaction.guild_id)
        cfg["enabled"] = True
        config.save(interaction.guild_id, cfg)
        await interaction.response.send_message("已啟用重複貼文偵測。", ephemeral=True)

    @repost.command(name="disable", description="停用偵測")
    async def disable(self, interaction: discord.Interaction):
        cfg = config.load(interaction.guild_id)
        cfg["enabled"] = False
        config.save(interaction.guild_id, cfg)
        await interaction.response.send_message("已停用重複貼文偵測。", ephemeral=True)

    @repost.command(name="ttl", description="設定索引保留天數")
    @app_commands.describe(days="保留天數（0 表示下次清理時全部清除）")
    async def ttl(self, interaction: discord.Interaction, days: app_commands.Range[int, 0, 3650]):
        cfg = config.load(interaction.guild_id)
        cfg["ttl_days"] = days
        config.save(interaction.guild_id, cfg)
        await interaction.response.send_message(f"索引保留天數已設為 {days} 天。", ephemeral=True)

    @repost.command(name="status", description="顯示目前設定")
    async def status(self, interaction: discord.Interaction):
        cfg = config.load(interaction.guild_id)
        whitelist = cfg.get("whitelist_channels") or []
        if whitelist:
            channels = "、".join(f"<#{cid}>" for cid in whitelist)
        else:
            channels = "全部頻道"
        lines = [
            f"狀態：{'啟用' if cfg.get('enabled', True) else '停用'}",
            f"監測頻道：{channels}",
            f"索引保留：{cfg.get('ttl_days', 30)} 天",
            f"已記錄項目：{db.count(interaction.guild_id)} 筆",
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @channel.command(name="add", description="新增白名單頻道")
    async def channel_add(self, interaction: discord.Interaction, channel: discord.TextChannel):
        cfg = config.load(interaction.guild_id)
        whitelist = cfg.get("whitelist_channels") or []
        if channel.id in whitelist:
            await interaction.response.send_message(f"{channel.mention} 已在白名單中。", ephemeral=True)
            return
        whitelist.append(channel.id)
        cfg["whitelist_channels"] = whitelist
        config.save(interaction.guild_id, cfg)
        await interaction.response.send_message(f"已將 {channel.mention} 加入白名單。", ephemeral=True)

    @channel.command(name="remove", description="移除白名單頻道")
    async def channel_remove(self, interaction: discord.Interaction, channel: discord.TextChannel):
        cfg = config.load(interaction.guild_id)
        whitelist = cfg.get("whitelist_channels") or []
        if channel.id not in whitelist:
            await interaction.response.send_message(f"{channel.mention} 不在白名單中。", ephemeral=True)
            return
        whitelist.remove(channel.id)
        cfg["whitelist_channels"] = whitelist
        config.save(interaction.guild_id, cfg)
        await interaction.response.send_message(f"已將 {channel.mention} 移出白名單。", ephemeral=True)

    @channel.command(name="list", description="列出白名單頻道")
    async def channel_list(self, interaction: discord.Interaction):
        cfg = config.load(interaction.guild_id)
        whitelist = cfg.get("whitelist_channels") or []
        if not whitelist:
            await interaction.response.send_message("目前監測全部頻道（白名單為空）。", ephemeral=True)
            return
        channels = "、".join(f"<#{cid}>" for cid in whitelist)
        await interaction.response.send_message(f"白名單頻道：{channels}", ephemeral=True)

    @message.command(name="set", description="設定回覆訊息模板")
    @app_commands.describe(template="可用變數：{platform}、{author}、{link}")
    async def message_set(self, interaction: discord.Interaction, template: str):
        try:
            template.format(platform="", author="", link="")
        except (KeyError, IndexError, ValueError):
            await interaction.response.send_message(
                "模板格式錯誤，只能使用 {platform}、{author}、{link}。", ephemeral=True
            )
            return
        cfg = config.load(interaction.guild_id)
        cfg["reply_template"] = template
        config.save(interaction.guild_id, cfg)
        await interaction.response.send_message("回覆訊息模板已更新。", ephemeral=True)

    @message.command(name="reset", description="還原預設回覆訊息")
    async def message_reset(self, interaction: discord.Interaction):
        cfg = config.load(interaction.guild_id)
        cfg["reply_template"] = config.DEFAULTS["reply_template"]
        config.save(interaction.guild_id, cfg)
        await interaction.response.send_message("回覆訊息已還原為預設。", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Admin(bot))

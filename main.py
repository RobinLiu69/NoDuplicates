import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import db

load_dotenv()
TOKEN = os.getenv("TOKEN")

COGS = ["cogs.detector", "cogs.admin"]


class RepostBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        db.connect()
        for cog in COGS:
            await self.load_extension(cog)
        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged on as {self.user}")


def main():
    if not TOKEN:
        print("TOKEN invalid.")
        return
    RepostBot().run(TOKEN)


if __name__ == "__main__":
    main()

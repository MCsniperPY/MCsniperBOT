import logging.handlers
import os
import sys
import traceback
from datetime import datetime

import discord
from discord.ext import commands

import config
from database_handler.postgres import DatabaseHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(asctime)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
    ],
)

start_time = datetime.now().strftime("%d/%m/%Y | %H:%M")


class MCsniperBOT(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=config.PREFIX,
            case_insensitive=True,
            intents=discord.Intents.all(),
        )
        self.database = DatabaseHandler

    async def on_ready(self):
        self.database.setup_tables()
        self.remove_command("help")
        await self.cog_loader()

    async def cog_loader(self, directory="./cogs"):
        for file in os.listdir(directory):
            if file.endswith(".py") and not file.startswith("_"):
                self.load_extension(f"{directory[2:].replace('/', '.')}.{file[:-3]}")
                print(f"=> {file[:-3]} Loaded")
            elif not (
                file in ["__pycache__"] or file.endswith(("pyc", "txt"))
            ) and not file.startswith("_"):
                print(f"[{file}]")
                await self.cog_loader(f"{directory}/{file}")

    async def on_command_error(self, ctx, error):
        ignored = (
            commands.CommandNotFound,
            commands.DisabledCommand,
            commands.NoPrivateMessage,
            commands.CheckFailure,
        )

        if isinstance(error, ignored):
            return

        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        log = await self.fetch_channel(config.LOGS_CHANNEL_ID)

        error_embed = discord.Embed(color=0x992D22)
        error_embed.title = "Command Error"
        error_embed.add_field(
            name="Author", value=f"{ctx.author} - {ctx.author.id}", inline=False
        )
        error_embed.add_field(name="Command", value=ctx.message.content, inline=False)
        error_embed.add_field(name="Error", value=error, inline=False)
        try:
            error_embed.add_field(
                name="Traceback",
                value="".join(
                    traceback.format_exception(
                        type(error), error.__cause__, error.__traceback__
                    )
                )[:1024],
                inline=False,
            )
        except AttributeError as e:
            print(e)
            error_embed.add_field(
                name="Traceback",
                value="Could not retrieve traceback...",
                inline=False,
            )
        error_embed.timestamp = datetime.utcnow()

        await log.send(embed=error_embed)

        logging.critical(f"Command produced error ({ctx.message.content}) :: {error}")


if __name__ == "__main__":
    MCsniperBOT().run(config.TOKEN)

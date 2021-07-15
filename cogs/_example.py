"""
each cog must go in a subdirectory of /cogs such as moderation, minecraft, or events.
"""
from discord.ext import commands


# import discord


class ExampleCog(commands.Cog):
    def __init__(self, client):
        self.client = client


def setup(client):
    client.add_cog(ExampleCog(client))

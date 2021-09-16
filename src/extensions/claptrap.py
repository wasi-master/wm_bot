"""Claptrap cog"""
import os
import random

import discord
from discord.ext import commands

from utils.errors import print_error
from utils.functions import load_json


class Claptrap(commands.Cog):
    """Absurd nonsensical talk"""

    def __init__(self, bot):
        self.bot = bot
        self.claptraps = load_json("assets/data/claptraps.json")

    @commands.command(aliases=["ct"], extras={"image": "https://i.imgur.com/igq43W3.png"})
    async def claptrap(self, ctx):
        """Can I shoot something now? Or climb some stairs? SOMETHING exciting? (has 500+ texts. can you get them all?)"""

        if not isinstance(self.claptraps, list):
            print_error("The [yellow]claptraps.json[/] file is not a list.")
            return await ctx.send("An error occurred. Check the console for more information.")

        await ctx.send(random.choice(self.claptraps))


def setup(bot):
    """Adds the cog to the bot"""
    if "claptraps.json" in os.listdir("assets/data"):
        bot.add_cog(Claptrap(bot))
    else:
        print_error(
            "The claptrap cog can't load because the file [underline yellow]assets/data/claptraps.json[/] is missing, "
            "please add it or edit the source code to change the path of the file"
        )

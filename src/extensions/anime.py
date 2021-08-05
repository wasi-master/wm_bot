import ast
import asyncio

import discord
from bs4 import BeautifulSoup
from discord.ext import commands


class Anime(commands.Cog):
    """Anime commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Sends a waifu")
    @commands.is_nsfw()
    async def waifu(self, ctx):
        """Sends [Waifu](https://www.dictionary.com/e/fictional-characters/waifu) pictures
        Note: This command is nsfw only"""

        gender = "male"
        async with ctx.typing():
            while gender == "male":
                async with self.bot.session.get("https://mywaifulist.moe/random") as resp:
                    response = await resp.text()
                soup = BeautifulSoup(response, "html.parser")
                image_url = ast.literal_eval(
                    "{" + str(soup.find("script", type="application/ld+json")).split("\n      ")[3].split(",")[0] + "}"
                )["image"]
                name = ast.literal_eval(
                    "{" + str(soup.find("script", type="application/ld+json")).split("\n      ")[4].split(",")[0] + "}"
                )["name"]
                gender = ast.literal_eval(
                    "{" + str(soup.find("script", type="application/ld+json")).split("\n      ")[5].split(",")[0] + "}"
                )["gender"]
            embed = discord.Embed(title=name.replace("&quot;", '"'), color=0x2F3136)
            embed.set_image(url=image_url)

        message = await ctx.send(embed=embed)
        await message.add_reaction("\u2764\ufe0f")

        def check(r, u):  # r = discord.Reaction, u = discord.Member or discord.User.
            return u.id == ctx.author.id and r.message.channel.id == ctx.channel.id

        try:
            reaction = await self.bot.wait_for("reaction_add", check=check, timeout=10)
        except asyncio.TimeoutError:
            try:
                return await message.clear_reactions()
            except discord.Forbidden:
                return await message.remove_reaction("\u2764\ufe0f", ctx.guild.me)
        else:
            if str(reaction.emoji) == "\u2764\ufe0f":
                embed.set_footer(icon_url=ctx.author.avatar.url, text=f"Claimed by {ctx.author.name}")
                await message.edit(embed=embed)
                return await ctx.send(
                    f":couple_with_heart: {ctx.author.mention} is now married with"
                    "**{name.replace('&quot;', '')}** :couple_with_heart:"
                )


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Anime(bot))

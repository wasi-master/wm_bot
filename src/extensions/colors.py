import json

import discord
from discord.ext import commands

from utils import randomcolor


class Colors(commands.Cog):
    """Color releated commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["col", "colour"], extras={"image": "https://i.imgur.com/zMQ7mz3.png"})
    async def color(self, ctx, color: commands.ColourConverter):
        """Sends information about a color
        The following formats are accepted:

        - `0x<hex>`
        - `#<hex>`
        - `0x#<hex>`
        - `rgb(<number>, <number>, <number>)`
        - All the colors mentioned in https://gist.github.com/Soheab/d9cf3f40e34037cfa544f464fc7d919e#colours
        """
        hexcol = str(hex(color.value))[2:]
        async with self.bot.session.get(f"http://www.thecolorapi.com/id?hex={hexcol}") as response:
            data = json.loads(await response.text())

        color_name = data["name"]["value"].title()
        intcol = int(hexcol, 16)

        embed = discord.Embed(color=intcol)
        embed.set_author(name=color_name)
        embed.set_image(url=f"http://singlecolorimage.com/get/{hexcol}/384x384")
        embed.add_field(name="Hex", value=data["hex"]["value"])
        embed.add_field(name="RGB", value=data["rgb"]["value"])
        embed.add_field(name="INT", value=intcol)
        embed.add_field(name="HSL", value=data["hsl"]["value"])
        embed.add_field(name="HSV", value=data["hsv"]["value"])
        embed.add_field(name="CMYK", value=data["cmyk"]["value"])
        embed.add_field(name="XYZ", value=data["XYZ"]["value"])
        await ctx.send(embed=embed)

    @color.error
    async def color_error(self, ctx, error):
        if isinstance(error, commands.BadColourArgument):
            return await ctx.send(f"Bad color: {error}")
        raise error

    @commands.command(
        aliases=["randcolor", "randomcol", "randcol", "randomcolor", "rc"],
        extras={"image": "https://i.imgur.com/m6GQHPg.png"},
    )
    async def randomcolour(self, ctx):
        """
        Generates a random color.
        Note: This is not fully random, but it is random enough for most purposes.
        """
        rand_color = randomcolor.RandomColor()
        generated_color = rand_color.generate()[0]
        hexcol = generated_color.replace("#", "")
        async with self.bot.session.get(f"http://www.thecolorapi.com/id?hex={hexcol}") as response:
            data = json.loads(await response.text())
        color_name = data["name"]["value"]
        rgb = data.get("rgb").get("value")
        hexcol = data.get("hex").get("value")
        intcol = int(hexcol[1:], 16)
        embed = discord.Embed(color=intcol)
        embed.set_author(name=color_name)
        embed.set_thumbnail(url=f"http://singlecolorimage.com/get/{hexcol[1:]}/256x256")
        embed.add_field(name="Hex", value=data["hex"]["value"])
        embed.add_field(name="RGB", value=data["rgb"]["value"])
        embed.add_field(name="INT", value=intcol)
        embed.add_field(name="HSL", value=data["hsl"]["value"])
        embed.add_field(name="HSV", value=data["hsv"]["value"])
        embed.add_field(name="CMYK", value=data["cmyk"]["value"])
        embed.add_field(name="XYZ", value=data["XYZ"]["value"])
        embed.set_footer(text="You can use the color command to get more details about the color")
        await ctx.send(embed=embed)


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Colors(bot))

"""Animals Cog"""
import discord
from discord.ext import commands


class Animals(commands.Cog):
    """Sends a random cute picture of animals"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["kitty"], extras={"image": "https://i.imgur.com/J8vTsyK.gif"})
    async def cat(self, ctx):
        """Sends a random random cute cat picture"""
        url = "https://some-random-api.ml/animal/cat"

        async with self.bot.session.get(url) as response:
            parsed_json = await response.json()
        img_url = parsed_json["image"]
        await ctx.send(
            embed=discord.Embed(title="Heres a cat picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + parsed_json["fact"])
        )

    @commands.command(aliases=["doggo", "puppy"], extras={"image": "https://i.imgur.com/nJIyoLq.gif"})
    async def dog(self, ctx):
        """Sends a random random cute dog picture"""
        url = "https://some-random-api.ml/animal/dog"

        async with self.bot.session.get(url) as response:
            parsed_json = await response.json()
        img_url = parsed_json["image"]
        await ctx.send(
            embed=discord.Embed(title="Heres a dog picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + parsed_json["fact"])
        )

    @commands.command(aliases=["pnd"], extras={"image": "https://i.imgur.com/GjsQ5AB.gif"})
    async def panda(self, ctx):
        """Sends a random random cute panda picture"""
        url = "https://some-random-api.ml/animal/panda"

        async with self.bot.session.get(url) as response:
            parsed_json = await response.json()
        img_url = parsed_json["image"]
        await ctx.send(
            embed=discord.Embed(title="Heres a panda picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + parsed_json["fact"])
        )

    @commands.command(aliases=["rdpnd"], extras={"image": "https://i.imgur.com/jgjohiu.gif"})
    async def redpanda(self, ctx):
        """Sends a random random cute red panda picture"""
        url = "https://some-random-api.ml/animal/red_panda"

        async with self.bot.session.get(url) as response:
            parsed_json = await response.json()
        img_url = parsed_json["image"]
        if not parsed_json.get("fact"):
            return await ctx.send(embed=discord.Embed(title="Heres a red panda picture").set_image(url=img_url))
        await ctx.send(
            embed=discord.Embed(title="Heres a red panda picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + parsed_json["fact"])
        )

    @commands.command(aliases=["kl"], extras={"image": "https://i.imgur.com/y8VhA8d.gif"})
    async def koala(self, ctx):
        """Sends a random cute koala picture"""
        url = "https://some-random-api.ml/animal/koala"

        async with self.bot.session.get(url) as response:
            parsed_json = await response.json()
        img_url = parsed_json["image"]
        if not parsed_json.get("fact"):
            return await ctx.send(embed=discord.Embed(title="Heres a koala picture").set_image(url=img_url))
        await ctx.send(
            embed=discord.Embed(title="Heres a koala picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + parsed_json["fact"])
        )

    @commands.command(aliases=["birb"], extras={"image": "https://i.imgur.com/wittKiF.gif"})
    async def bird(self, ctx):
        """Sends a random cute bird picture"""
        url = "https://some-random-api.ml/animal/birb"

        async with self.bot.session.get(url) as response:
            parsed_json = await response.json()
        img_url = parsed_json["image"]
        await ctx.send(
            embed=discord.Embed(title="Heres a bird picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + parsed_json["fact"])
        )

    @commands.command(aliases=["rcn"], extras={"image": "https://i.imgur.com/u7xuVvG.gif"})
    async def racoon(self, ctx):
        """Sends a random racoon picture"""
        url = "https://some-random-api.ml/animal/racoon"

        async with self.bot.session.get(url) as response:
            parsed_json = await response.json()
        img_url = parsed_json["image"]
        if not parsed_json.get("fact"):
            return await ctx.send(embed=discord.Embed(title="Heres a racoon picture").set_image(url=img_url))
        await ctx.send(
            embed=discord.Embed(title="Heres a racoon picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + parsed_json["fact"])
        )

    @commands.command(aliases=["kng"], extras={"image": "https://i.imgur.com/rPvwWVW.gif"})
    async def kangaroo(self, ctx):
        "Sends a random kangaroo picture"
        url = "https://some-random-api.ml/animal/kangaroo"

        async with self.bot.session.get(url) as response:
            parsed_json = await response.json()
        img_url = parsed_json["image"]
        if not parsed_json.get("fact"):
            return await ctx.send(embed=discord.Embed(title="Heres a kangaroo picture").set_image(url=img_url))
        await ctx.send(
            embed=discord.Embed(title="Heres a kangaroo picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + parsed_json["fact"])
        )

    @commands.command(aliases=["fx"], extras={"image": "https://i.imgur.com/eHN5GZT.gif"})
    async def fox(self, ctx):
        "Sends a random high quality fox picture"
        url = "https://randomfox.ca/floof/"

        async with self.bot.session.get(url) as response:
            parsed_json = await response.json()
        img_url = parsed_json["image"]
        await ctx.send(embed=discord.Embed(title="Heres a fox picture").set_image(url=img_url))


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Animals(bot))

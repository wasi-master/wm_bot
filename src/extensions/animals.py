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
        # Fetch image from TheCatAPI
        async with self.bot.session.get("https://api.thecatapi.com/v1/images/search") as response:
            parsed_json = await response.json()
        img_url = parsed_json[0]["url"]

        # Fetch fact from catfact.ninja
        async with self.bot.session.get("https://catfact.ninja/fact") as response:
            fact_json = await response.json()
        fact = fact_json["fact"]

        await ctx.send(
            embed=discord.Embed(title="Heres a cat picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + fact)
        )

    @commands.command(aliases=["doggo", "puppy"], extras={"image": "https://i.imgur.com/nJIyoLq.gif"})
    async def dog(self, ctx):
        """Sends a random random cute dog picture"""
        # Fetch image from Dog CEO API
        async with self.bot.session.get("https://dog.ceo/api/breeds/image/random") as response:
            parsed_json = await response.json()
        img_url = parsed_json["message"]

        # Fetch fact from dogapi.dog
        async with self.bot.session.get("https://dogapi.dog/api/v2/facts") as response:
            fact_json = await response.json()
        fact = fact_json["data"][0]["attributes"]["body"]

        await ctx.send(
            embed=discord.Embed(title="Heres a dog picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + fact)
        )

    @commands.command(aliases=["pnd"], extras={"image": "https://i.imgur.com/GjsQ5AB.gif"})
    async def panda(self, ctx):
        """Sends a random random cute panda picture"""
        # Fetch image and fact from pandaa.vercel.app
        async with self.bot.session.get("https://pandaa.vercel.app/all") as response:
            parsed_json = await response.json()
        img_url = parsed_json["pic"]
        fact = parsed_json.get("fact")

        embed = discord.Embed(title="Heres a panda picture").set_image(url=img_url)
        if fact:
            embed.set_footer(text="Fun Fact: " + fact)
        await ctx.send(embed=embed)

    @commands.command(aliases=["quack"], extras={"image": "https://i.imgur.com/jgjohiu.gif"})
    async def duck(self, ctx):
        """Sends a random cute duck picture"""
        # Fetch image from random-d.uk
        async with self.bot.session.get("https://random-d.uk/api/v2/random") as response:
            parsed_json = await response.json()
        img_url = parsed_json["url"]
        await ctx.send(embed=discord.Embed(title="Heres a duck picture").set_image(url=img_url))

    @commands.command(aliases=["bunny"], extras={"image": "https://i.imgur.com/y8VhA8d.gif"})
    async def rabbit(self, ctx):
        """Sends a random cute rabbit picture"""
        # Fetch image from animals.maxz.dev
        async with self.bot.session.get("https://animals.maxz.dev/api/rabbit/random") as response:
            parsed_json = await response.json()
        img_url = parsed_json["image"]
        await ctx.send(embed=discord.Embed(title="Heres a rabbit picture").set_image(url=img_url))

    @commands.command(aliases=["birb"], extras={"image": "https://i.imgur.com/wittKiF.gif"})
    async def bird(self, ctx):
        """Sends a random cute bird picture"""
        # Fetch image from shibe.online
        async with self.bot.session.get(
            "https://shibe.online/api/birds", params={"count": 1, "urls": "true", "httpsUrls": "true"}
        ) as response:
            parsed_json = await response.json()
        img_url = parsed_json[0]
        await ctx.send(embed=discord.Embed(title="Heres a bird picture").set_image(url=img_url))

    @commands.command(aliases=["capy"], extras={"image": "https://i.imgur.com/u7xuVvG.gif"})
    async def capybara(self, ctx):
        """Sends a random capybara picture"""
        # Fetch image from animals.maxz.dev
        async with self.bot.session.get("https://animals.maxz.dev/api/capybara/random") as response:
            parsed_json = await response.json()
        img_url = parsed_json["image"]
        await ctx.send(embed=discord.Embed(title="Heres a capybara picture").set_image(url=img_url))

    @commands.command(aliases=["shibe"], extras={"image": "https://i.imgur.com/rPvwWVW.gif"})
    async def shiba(self, ctx):
        """Sends a random shiba inu picture"""
        # Fetch image from shibe.online
        async with self.bot.session.get(
            "https://shibe.online/api/shibes", params={"count": 1, "urls": "true", "httpsUrls": "true"}
        ) as response:
            parsed_json = await response.json()
        img_url = parsed_json[0]
        await ctx.send(embed=discord.Embed(title="Heres a shiba inu picture").set_image(url=img_url))

    @commands.command(aliases=["fx"], extras={"image": "https://i.imgur.com/eHN5GZT.gif"})
    async def fox(self, ctx):
        "Sends a random high quality fox picture"
        url = "https://randomfox.ca/floof/"

        async with self.bot.session.get(url) as response:
            parsed_json = await response.json()
        img_url = parsed_json["image"]
        await ctx.send(embed=discord.Embed(title="Heres a fox picture").set_image(url=img_url))


async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(Animals(bot))

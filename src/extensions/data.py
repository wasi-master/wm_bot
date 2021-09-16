import json
import re
from datetime import datetime
from io import BytesIO
from urllib.parse import quote

import discord
from discord.ext import commands
from discord.ext.commands import BucketType

from utils.errors import NoAPIKey
from utils.paginator import Paginator


def unique(input):
    output = []
    for x in input:
        if x not in output:
            output.append(x)
    return output


class Data(commands.Cog):
    """Commands to get some data"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["lrc"])
    @commands.bot_has_permissions(use_external_emojis=True)
    async def lyrics(self, ctx, *, song_name: str):
        """Sends the lyrics of a song"""
        # We get the actual json response
        async with self.bot.session.get(f"https://some-random-api.ml/lyrics", params={"title": song_name}) as cs:
            fj = await cs.json()
        # We make a paginator in case the song is more than 2048 characters
        paginator = commands.Paginator(prefix="", suffix="", max_size=2048)
        # We make a pages variable to store the embeds
        pages = []
        # For each line in the lyrics, we add that line to the paginator
        for line in fj["lyrics"].splitlines():
            paginator.add_line(line)
        # Now for each page, we need to add a embed with the contents of the page to the pages list
        for page in paginator.pages:
            embed = discord.Embed(
                title=fj["title"],
                description=page,
                url=list(fj["links"].values())[0],
            )
            embed.set_thumbnail(url=list(fj["thumbnail"].values())[0])
            embed.set_author(name=fj["author"])
            pages.append(embed)
        # now we create our custom paginator that uses reactions
        paginator = Paginator(pages)
        # and we start our custom paginator
        await paginator.start(ctx)

    @commands.command(aliases=["pd"])
    @commands.bot_has_permissions(use_external_emojis=True)
    async def pokedex(self, ctx, pokemon: str):
        """Sends the details about a [pokemon](https://en.wikipedia.org/wiki/Pok%C3%A9mon)"""
        # We encode the song name for the web request
        pokemon = quote(pokemon)
        # We get the actual json response
        async with self.bot.session.get(f"https://some-random-api.ml/pokedex", params={"pokemon": pokemon}) as cs:
            fj = await cs.json()
        # We get the stats key and save it to a variable named stats
        stats = fj["stats"]
        # We add the details of the pokemon to the embed
        embed = discord.Embed(title=fj["name"].title(), description=fj["description"])
        embed.add_field(name="Type", value=", ".join(fj["type"]))
        embed.add_field(name="Abilities", value=", ".join(fj["abilities"]))
        embed.add_field(
            name="Stats",
            value=f"Height: {fj['height']}\nWeight: {fj['weight']}\nGender Ratio:\n        Male: {fj['gender'][0][:-5]}\n        Female:{fj['gender'][1][:-7]}",
            inline=False,
        )
        embed.add_field(
            name="More Stats",
            value=f"HP: {stats['hp']}\nAttack: {stats['attack']}\nDefense: {stats['defense']}\nSpecial Attack: {stats['sp_atk']}\nSpecial Defense: {stats['sp_def']}\nSpeed: {stats['speed']}\n**Total**: {stats['total']}",
            inline=False,
        )
        embed.add_field(
            name="Evoloution",
            value="\n".join(unique(fj["family"]["evolutionLine"])).replace(
                fj["family"]["evolutionLine"][fj["family"]["evolutionStage"] - 1],
                f'**{fj["family"]["evolutionLine"][fj["family"]["evolutionStage"]-1]}**',
            ),
            inline=False,
        )
        embed.set_thumbnail(url=fj["sprites"]["animated"])
        # Now we send the embed
        await ctx.send(embed=embed)

    @commands.command(description="Coronavirus Stats")
    async def covid(self, ctx, *, area: str = None):
        """Sends statistics about the corona virus situation of a country
        The area defaults to `global` if not specified"""
        formatted_json = None

        async with self.bot.session.get("https://api.covid19api.com/summary") as r:
            fj = await r.json()

        if area is None:
            formatted_json = fj["Global"]
        else:
            #! I probably need to refactor this code but i'm too tired to do it right now
            for i in fj["Countries"]:
                if i["Slug"].lower() == area.lower():
                    formatted_json = i
                    break
                else:
                    continue

        if formatted_json is None:
            return await ctx.send("Country not found")

        embed = discord.Embed(
            title=f"Covid 19 Stats ({area.title()})",
            color=0x2F3136,
            timestamp=datetime.strptime(formatted_json["Date"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        embed.add_field(name="New Cases", value=f"{formatted_json['NewConfirmed']:,}")
        embed.add_field(name="Total Cases", value=f"{formatted_json['TotalConfirmed']:,}")
        embed.add_field(name="New Deaths", value=f"{formatted_json['NewDeaths']:,}")
        embed.add_field(name="Total Deaths", value=f"{formatted_json['TotalDeaths']:,}")
        embed.add_field(name="New Recovered", value=f"{formatted_json['NewRecovered']:,}")
        embed.add_field(name="Total Recovered", value=f"{formatted_json['TotalRecovered']:,}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["randomfact", "rf", " f"])
    async def fact(self, ctx):
        """Sends a random fact"""

        async with self.bot.session.get("https://uselessfacts.jsph.pl/random.json?language=en") as resp:
            fj = json.loads(await resp.text())

        embed = discord.Embed(title="Random Fact", description=fj["text"], color=0x2F3136)
        await ctx.send(embed=embed)

    @commands.command(description="See details about a movie")
    async def movie(self, ctx, *, query):
        """Sends information about a movie"""
        # We need an api key to use the omdb api
        apikey = self.bot.api_keys.get("OMDB")
        if not apikey:
            raise NoAPIKey

        url = f"http://www.omdbapi.com/?i=tt3896198&apikey={apikey}&t={query}&__cf_chl_captcha_tk__=fca02a1342e0659935058a7d465492ed7a8491d1-1624343613-0-AUWpCsdbhSi8op9Jxs83r0s9SoRB8amrkdvxWqXXL6bcNTep_iKG0g9jjy_7xpxx8BGUvp8FwiI2pvH-ckjcRnsConKxWIsAwTicu1mRxK1CFSbpaTAjVoXjvD_RSCvubRRApIyX8JtUubS_CQHuMHXEvP1Ujf-UWIhlhKKN8kOHffVfTS6UKVcgC8-7P5WZPVb7BsenT_nJjAyDy-PBAZIL7ft30DlMn1IftIOfvzmY1CkMN30mLeY7B2DLo8nUOy7ZxeOeq2n93RnxKjXwA72Ylz92WsRn-Mh5N6zmH3EzXxfFMWeSqrMEwvQfnoaXTNVDr0uVVMXuQ_kWcDt7OfaG5Y7-p6r8K3srRmvy8rTZM739SiVetAcXnb0EO29Di5zA0Ta9vAOVXs0kDgGZI0Y4SYD3UQRV2u95iL7vH9ofW4hRxZjugqLZUD_Y7WZ-wLMaKGOhqAG1CAPlSyeSprE-KF6by43QxOg2czBQeKd24ZpMjtcmhOYCzFBUs1KWlAncU5RzzknFHdsxnFTCsWK3itB2OJz8oRHXQqFSL3oanuClhARZcyrKWf5XYVtdCiWD01uDAQZk6J6dOcvdpkVJgpfugMUAAkS7ehbALP4t4hhhHsDpI61PlfPKg_t-mkWTyDEsC8q7G5wQSD0LhTc5WKsvybqnMso5daiJvy6D"
        async with self.bot.session.get(url) as response:
            fj = json.loads(await response.text())

        if fj["Response"] == "True":
            embed = discord.Embed(title=fj["Title"], description=fj["Plot"], color=0x2F3136)
            # We use regex to validate the poster since it may sometimes contain an invalid poster
            if re.search(r"(http(s?):)(.)*\.(?:jpg|gif|png)", fj["Poster"]):
                embed.set_image(url=fj["Poster"])

            embed.add_field(name="Released On", value=fj["Released"])
            embed.add_field(name="Rated", value=fj["Rated"])
            embed.add_field(name="Duration", value=f"{fj['Runtime']}")
            embed.add_field(name="Genre", value=fj["Genre"])
            embed.add_field(
                name="Credits",
                value=f"**Director**: {fj['Director']}\n**Writer**: {fj['Writer']}\n**Casts**: {fj['Actors']}",
            )
            embed.add_field(name="Language(s)", value=fj["Language"])
            embed.add_field(
                name="IMDB",
                value=f"Rating: {fj['imdbRating']}\nVotes: {fj['imdbVotes']}",
            )
            embed.add_field(name="Production", value=f"[{fj['Production']}]({fj['Website']})")
            await ctx.send(embed=embed)
        else:
            await ctx.send("Movie Not Found")

    @commands.command(name="screenshot", aliases=["ss"])
    async def ss(self, ctx, website: str):
        """Sends the screenshot of a website"""
        # We strip embed markers
        website = website.strip("<>")
        # We use thum.io for the screenshot
        image_url = f"https://image.thum.io/get/width/1920/crop/675/maxAge/1/noanimate/{website}"
        async with self.bot.session.get(image_url) as r:
            raw_image = BytesIO(await r.read())
        # We use an api to detect inappropriate content
        async with self.bot.session.post(
            # This api key is not mine so idc
            # I got this api key from a website that used this.
            "https://api.haystack.ai/api/image/analyze?apikey=515341b03fb97255d0e9f2b6d33dc9ea&output=json&model=AdultType",
            data={
                "image": raw_image.read(),
            },
        ) as resp:
            # We get the actual nsfw details
            response_json = json.loads(await resp.text())
            if not response_json.get("adultContent"):
                return await ctx.send("no")
            nsfw_score = response_json["adultContent"]["isAdultContentConfidence"]
            is_nsfw = response_json["adultContent"]["isAdultContent"]
        if is_nsfw:
            # If the screenshot is nsfw then we just send no.
            # I may change this later to show the nsfw score
            return await ctx.send("no")
        # If everything went fine then we send the screenshot
        return await ctx.reply(
            embed=discord.Embed(title=website, url=website).set_image(
                url=f"https://image.thum.io/get/width/1920/crop/675/maxAge/1/noanimate/{website}"
            ),
        )

    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def gender(self, ctx, *, name: str):
        """Get the gender of the person with the name specified"""
        # This command was made like long time ago and I just don't wanna remove it
        # but I also don't wanna use an api to do this so idk
        try:
            api_key = self.bot.api_keys["gender_api"]
        except KeyError:
            raise NoAPIKey

        url = f"https://gender-api.com/get"
        async with self.bot.session.get(url, params={"name": "name", "key": api_key}) as r:
            fj = json.loads(await r.text())

        # Getting the gender and assigning color corresponding to the gender
        if fj["gender"] == "male":
            gender = "Male"
            color, gender = 0x2CB4FF, "Male"
        elif fj["gender"] == "female":
            gender, color = "Female", 0xFF2CB4
        else:
            gender, color = "Unknown", 0x646464

        #! Now this may also need some refactoring
        positive = str(fj["accuracy"]) + "%"
        negative = str(100 - fj["accuracy"]) + "%"
        if gender != "Unknown":
            text = f"The name {fj['name_sanitized']} has a **{positive}** chance of being a  **{gender}** and a {negative} chance of not being a {gender}"
        else:
            text = f"The name {fj['name_sanitized']} is not in our database"
        embed = discord.Embed(title=fj["name_sanitized"], description=text, color=color)
        await ctx.send(embed=embed)

    @commands.command()
    async def weather(self, ctx, *, location: str):
        """Sends the weather information of a specific location"""
        # We need an api key to use the open weather map api
        try:
            api_key = self.bot.api_keys["open_weather_map"]
        except KeyError:
            raise NoAPIKey

        url = f"http://api.openweathermap.org/data/2.5/weather"
        async with self.bot.session.get(url, params={"q": location, "APPID": api_key}) as r:
            fj = json.loads(await r.text())

        if fj["cod"] == "404":
            return await ctx.send("Location not found")
        if fj["cod"] != "404":
            embed = discord.Embed(
                title=fj["name"],
                description=f'**{fj["weather"][0]["main"]}**\n{fj["weather"][0]["description"]}',
                color=0x2F3136,
            )
            embed.add_field(
                name="Temperature",
                value=f'Main: {round(fj["main"]["temp"] - 273.15, 2)}°C\nFeels Like: {round(fj["main"]["feels_like"] - 273.15, 2)}°C',
            )
            embed.add_field(
                name="Wind",
                value=f'Speed: {fj["wind"]["speed"]}Kmh\nDirection: {fj["wind"]["deg"]}°',
            )
            embed.add_field(name="Cloudyness", value=str(fj["clouds"]["all"]) + "%")
            # * embed.add_field(name="Sun", value=f'Sunrise: {datetime.datetime.fromtimestamp(fj["sys"]["sunrise"]).strftime("%I:%M:%S")}\nSunset: {datetime.datetime.fromtimestamp(fj["sys"]["sunset"]).strftime("%I:%M:%S")}')
            await ctx.send(embed=embed)
        else:
            await ctx.send("Service down")


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Data(bot))

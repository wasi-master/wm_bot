from typing import Literal, Optional
import discord
from discord.ext import commands
from utils.converters import CustomLiteral
from utils.paginator import Paginator
from datetime import datetime
from io import BytesIO
import json
import random

class Space(commands.Cog):
    """Commands that are releated to outer space"""
    def __init__(self, bot):
        self.bot = bot
        self.api_key = bot.api_keys["nasa"] or "DEMO_KEY"

    @commands.command(aliases=["apod", "astrography-photo-of-the-day"])
    async def astrographyphotooftheday(self, ctx, date=None):
        params = dict(api_key=self.api_key)
        if date: params["date"] = date
        async with self.bot.session.get("https://api.nasa.gov/planetary/apod", params=params) as r:
            resp = await r.json()
            _copyright = f"\n©️ {resp['copyright']}" if resp.get("copyright") else ""
        embed = discord.Embed(title=resp["title"], description=resp["explanation"], color=discord.Colour.random())
        embed.set_image(url=resp.get("hdurl") or resp.get("url"))
        embed.set_footer(text=f"Taken at {resp['date']}{_copyright}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["neo", "near-earth-object"])
    async def nearearthobject(self, ctx, date=None):
        params = dict(api_key=self.api_key)
        if date:
            params["start_date"] = date
            params["end_date"] = date
        async with self.bot.session.get("https://api.nasa.gov/neo/rest/v1/feed", params=params) as r:
            resp = await r.json()
        embeds = []
        for obj in list(resp["near_earth_objects"].items())[0][1]:
            embed = discord.Embed(title=obj["name"], url=obj["nasa_jpl_url"], color=discord.Colour.green() if not obj["is_potentially_hazardous_asteroid"] else discord.Colour.red())
            embed.add_field(
                name="Estimated Diameter",
                value=(
                    f"Kilometer: {round(float(obj['estimated_diameter']['kilometers']['estimated_diameter_min']), 2):,} to {round(float(obj['estimated_diameter']['kilometers']['estimated_diameter_max']), 2):,}\n"
                    f"Meter: {round(float(obj['estimated_diameter']['meters']['estimated_diameter_min']), 2):,} to {round(float(obj['estimated_diameter']['meters']['estimated_diameter_max']), 2):,}\n"
                    f"Mile: {round(float(obj['estimated_diameter']['miles']['estimated_diameter_min']), 2):,} to {round(float(obj['estimated_diameter']['miles']['estimated_diameter_max']), 2):,}\n"
                    f"Feet: {round(float(obj['estimated_diameter']['feet']['estimated_diameter_min']), 2):,} to {round(float(obj['estimated_diameter']['feet']['estimated_diameter_max']), 2):,}"
                )
            )
            if obj['close_approach_data']:
                embed.add_field(
                    name="Close Approach",
                    value=(
                        f"Time: <t:{obj['close_approach_data'][0]['epoch_date_close_approach']//1000}:f> (<t:{obj['close_approach_data'][0]['epoch_date_close_approach']//1000}:R>)\n"
                        f"Speed: {round(float(obj['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']), 2):,} kmph ({round(float(obj['close_approach_data'][0]['relative_velocity']['miles_per_hour']), 2):,} mph\n"
                        f"Miss Distance: {round(float(obj['close_approach_data'][0]['miss_distance']['astronomical']), 2):,} AU or {round(float(obj['close_approach_data'][0]['miss_distance']['lunar']), 2):,} LD or {round(float(obj['close_approach_data'][0]['miss_distance']['kilometers']), 2):,} KM or {round(float(obj['close_approach_data'][0]['miss_distance']['miles']), 2):,} M"
                    )
                )
            embeds.append(embed)
        pag = Paginator(embeds)
        await pag.start(ctx)

    @commands.command(aliases=["epic", "earth-polychromatic-imaging-camera"])
    async def earthpolychromaticimagingcamera(self, ctx, filter: Literal["natural", "natural/all", "natural/available", "enhanced", "enhanced/all", "enhanced/available"]="natural"):
        params = dict(api_key=self.api_key)
        async with self.bot.session.get("https://api.nasa.gov/EPIC/api/" + filter, params=params) as r:
            resp = await r.json()
        embeds = []

        for image in resp:
            taken_at = datetime.fromisoformat(image["date"])
            embed = discord.Embed(title=image['image'], description=image['caption'])
            embed.add_field(name="Date", value=f"{discord.utils.format_dt(taken_at, 'F')} ({discord.utils.format_dt(taken_at, 'R')})")
            # TODO: better formatting
            embed.add_field(name="Coordinates", value=f"```json\n{json.dumps(image['coords'], indent=4)}\n```", inline=False)
            date = taken_at.strftime("%Y/%m/%d")
            # We use the demo key because this is going in a embed and we don't want people to get our api key
            # We also don't just use bytesio because you can't add more than 10 files
            image_url = f"https://api.nasa.gov/EPIC/archive/{filter}/{date}/png/{image['image']}.png?api_key=DEMO_KEY"
            embed.set_image(url=image_url)
            embeds.append(embed)

        pag = Paginator(embeds)
        await pag.start(ctx)

    @commands.command(aliases=["rmrp", "remote-monitoring-repository"])
    async def randommarsroverphoto(self, ctx, rover_name: CustomLiteral("curiosity", "opportunity", "spirit")=None):
        rover_name = rover_name or random.choice(("curiosity", "opportunity", "spirit"))
        params = dict(
            api_key=self.api_key,
            # sol stands for Solar Date
            sol=random.randint(
                    0,
                    # curiosity is still running so the latest number can be higher than this.
                    # spirit and opportunity is not running so the images taken by those are gonna stay the same
                    {'curiosity': 3234, 'spirit': 2208, 'opportunity': 5107}[rover_name]
                )
            )
        async with self.bot.session.get(f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover_name}/photos", params=params) as r:
            resp = await r.json()
        embeds = []
        for image in resp["photos"]:
            earth_date = datetime.fromisoformat(image["earth_date"])
            embed = discord.Embed()
            embed.set_image(url=image["img_src"])
            embed.add_field(name="Date", value=f"{discord.utils.format_dt(earth_date, 'f')} ({discord.utils.format_dt(earth_date, 'R')})")
            # TODO: better formatting
            embed.add_field(name="Rover", value=f"```json\n{json.dumps(image['rover'], indent=4)}\n```", inline=False)
            embed.add_field(name="Camera", value=f"```json\n{json.dumps(image['rover'], indent=4)}\n```", inline=False)
            embeds.append(embed)
        pag = Paginator(embeds)
        await pag.start(ctx)


def setup(bot):
    bot.add_cog(Space(bot))

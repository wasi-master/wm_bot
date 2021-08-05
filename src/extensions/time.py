import asyncio
import datetime
import difflib
import json
from typing import Union

import discord
import humanize
from discord.ext import commands
from utils.converters import TimeConverter


class Time(commands.Cog):
    """Commands related to time"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def remind(self, ctx, time: TimeConverter, *, text: str):
        """Remind you to do something after the specified time."""
        natural_time = humanize.naturaldelta(datetime.timedelta(seconds=int(time)))
        await ctx.send(f"Gonna remind you `{text}` in {natural_time}")
        await asyncio.sleep(time)
        await ctx.author.send(text)

    @commands.command(
        aliases=["tzs", "timezoneset", "settimezone", "stz", "ts"],
    )
    async def timeset(self, ctx, *, timezone: str):
        """Set your time zone to be used in the time command"""
        location = timezone

        # Validate that the person did not just send a continent
        continents = ["asia", "europe", "oceania", "australia", "africa"]
        if location.lower() in continents:
            return await ctx.send("I need a area not a continent 🤦‍♂️")

        async with self.bot.session.get(f"http://worldtimeapi.org/api/timezone/{location}") as resp:
            fj = json.loads(await resp.text())

        # The error key exists only when there is a error
        if fj.get("error"):
            if fj["error"] == "unknown location":
                async with self.bot.session.get("http://worldtimeapi.org/api/timezone") as resp:
                    locations = await resp.json()

                suggestions = difflib.get_close_matches(location, locations, n=5, cutoff=0.3)
                suggestions = "\n".join(suggestions)

                embed = discord.Embed(
                    title="Unknown Location",
                    description="The location couldn't be found",
                    color=14885931,
                )
                embed.add_field(name="Did you mean?", value=suggestions)

                await ctx.send(embed=embed)
            else:
                await ctx.send(fj["error"])

        # FIXME: use a single query
        savedtimezone = await self.bot.db.fetchrow(
            """
            SELECT * FROM timezones
            WHERE user_id = $1
            """,
            ctx.author.id,
        )
        if not savedtimezone is None:
            savedtimezone = await self.bot.db.execute(
                """
                UPDATE timezones
                SET timezone = $2
                WHERE user_id = $1
                """,
                ctx.author.id,
                timezone,
            )
        else:
            await self.bot.db.execute(
                """
                INSERT INTO timezones (timezone, user_id)
                VALUES ($1, $2)
                """,
                timezone,
                ctx.author.id,
            )
        embed = discord.Embed(
            title="Success",
            description=f"Timezone set to {location}",
            color=5028631,
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["tm"], description="See time")
    async def time(self, ctx, location: Union[discord.Member, str] = None):
        """See someones time or your time

        The person needs to have their time zone saved
        """

        # If the location is None then we show the user's time
        if location is None:
            location_from_db = await self.bot.db.fetchrow(
                """
                SELECT * FROM timezones
                WHERE user_id = $1""",
                ctx.author.id,
            )
            if location_from_db is None:
                embed = discord.Embed(
                    title="Timezone Not set",
                    description='Set your time with the timeset command (shortest alias "ts")',
                    color=14885931,
                )
                return await ctx.send(embed=embed)
            location = location_from_db["location"]
        # If the author mentions a user then we show the mentioned user's time'
        if isinstance(location, discord.Member):
            location_from_db = await self.bot.db.fetchrow(
                """
                SELECT * FROM timezones
                WHERE user_id = $1
                """,
                location.id,
            )
            if location_from_db is None:
                embed = discord.Embed(
                    title=f"{location} Has not yet set is location",
                    description='Ask him to set his time with the timeset command (shortest alias "ts")',
                    color=14885931,
                )
                return await ctx.send(embed=embed)
            location = location_from_db["location"]

        async with self.bot.session.get(f"http://worldtimeapi.org/api/timezone/{location}") as r:
            fj = json.loads(await r.text())
        # If the location was passed as a string then it may be wrong so we check for that
        if isinstance(location, str):
            # The error key exists only when there is a error
            if fj.get("error"):
                if fj["error"] == "unknown location":
                    async with self.bot.session.get("http://worldtimeapi.org/api/timezone") as resp:
                        locations = await resp.json()

                    suggestions = difflib.get_close_matches(location, locations, n=5, cutoff=0.3)
                    suggestions = "\n".join(suggestions)

                    embed = discord.Embed(
                        title="Unknown Location",
                        description="The location couldn't be found",
                        color=14885931,
                    )
                    embed.add_field(name="Did you mean?", value=suggestions)

                    await ctx.send(embed=embed)
                else:
                    await ctx.send(fj["error"])

        currenttime = datetime.datetime.strptime(fj["datetime"][:-13], "%Y-%m-%dT%H:%M:%S")

        embed = discord.Embed(title="Time", color=0x2F3136)
        embed.add_field(name=location, value=currenttime.strftime("%a, %d %B %Y, %H:%M:%S"))
        embed.add_field(name="UTC Offset", value=fj["utc_offset"])

        await ctx.send(embed=embed)


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Time(bot))

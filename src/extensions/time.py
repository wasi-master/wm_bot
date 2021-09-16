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

        result = await self.bot.db.fetchrow(
            """
            INSERT INTO timezones (user_id, timezone)
                VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE
                SET timezone = EXCLUDED.timezone
            RETURNING *;
            """,
            ctx.author.id,
            timezone,
        )
        if result:
            if result["timezone"] == timezone:
                embed = discord.Embed(
                    title="Failure",
                    description=f"Time zone not changed, it was already set to {timezone}",
                    color=discord.Colour.red(),
                )
            else:
                embed = discord.Embed(
                    title="Success",
                    description=f"Time zone changed from `{result['timezone']}` to `{timezone}`",
                    color=discord.Colour.yellow(),
                )
        else:
            embed = discord.Embed(
                title="Success",
                description=f"Time zone set to `{timezone}`",
                color=discord.Colour.green(),
            )

        await ctx.send(embed=embed)

    @commands.command(aliases=["tm"], description="See time")
    async def time(self, ctx, location: Union[discord.Member, str] = None):
        """See someones time or your time

        The person needs to have their time zone saved
        """
        if location is None:
            location = ctx.author

        # If the item provided is a member then we get their location from the database
        if isinstance(location, discord.Member):
            # TODO: Cache
            result = await self.bot.db.fetchrow(
                """
                SELECT * FROM timezones
                WHERE user_id = $1""",
                location.id,
            )
            if result is None:
                embed = discord.Embed(
                    title=f"{location} Has not yet set is location",
                    description="He needs to set his timezone using the timeset command",
                    color=14885931,
                )
                return await ctx.send(embed=embed)
            location = result["timezone"]

        # We get the time
        async with self.bot.session.get(f"http://worldtimeapi.org/api/timezone/{location}") as r:
            fj = json.loads(await r.text())

        # If there was a error then we notify the user
        if fj.get("error") == "unknown location":
            async with self.bot.session.get("http://worldtimeapi.org/api/timezone") as resp:
                locations = await resp.json()
            suggestions = difflib.get_close_matches(location, locations, n=5, cutoff=0.3)
            suggestions = "\n".join(suggestions)
            embed = discord.Embed(
                title="Unknown Location", description="The location couldn't be found", color=14885931
            )
            embed.add_field(name="Did you mean?", value=suggestions)
            return await ctx.send(embed=embed)

        currenttime = datetime.datetime.strptime(fj["datetime"][:-13], "%Y-%m-%dT%H:%M:%S")
        embed = discord.Embed(title="Time", color=0x2F3136)
        embed.add_field(name=location, value=currenttime.strftime("%a, %d %B %Y, %H:%M:%S"))
        embed.add_field(name="UTC Offset", value=fj["utc_offset"])

        await ctx.send(embed=embed)


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Time(bot))

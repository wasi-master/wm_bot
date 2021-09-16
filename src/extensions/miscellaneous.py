import asyncio
import datetime
import re
from typing import Optional

import discord
from discord.ext import commands


class Miscellaneous(commands.Cog):
    """For commands that don't fit in any other category"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["speak", "echo", "s"])
    async def say(self, ctx, channel: Optional[discord.TextChannel] = None, *, text: commands.clean_content):
        """Says what you want the bot to say.

        If channel is specified then says the thing in that channel, if it is not specified then uses the current channel
        you can't mention people in the message
        """
        channel = channel or ctx.channel

        # If they have the manage messages permission then we delete their original message
        if channel.permissions_for(ctx.author).manage_messages:

            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass

            return await channel.send(text)
        # If the user wants to send the message in a specified channel then we want to say who sent the message
        if channel != ctx.channel:
            text = f"{text}\n\n    - sent by {ctx.author} from {ctx.channel.mention} ({ctx.message.jump_url})"

        m = await channel.send(text)

        def check(message):
            return message == ctx.message

        try:
            await self.bot.wait_for("message_delete", timeout=30, check=check)
        except asyncio.TimeoutError:
            pass
        else:
            if channel != ctx.channel:
                return await m.edit(
                    content=f"{text}\n\n    - sent by {ctx.author} from {ctx.channel.mention} but he deleted his original message 😒"
                )

            await m.edit(content=f"{text}\n\n    - sent by {ctx.author} but he deleted his message 😒")

    @commands.command(aliases=["webping", "pingweb", "wp", "pw"])
    async def websiteping(self, ctx, url: str):
        """"""
        # We do some validation
        if not url.startswith("http://") or url.startswith("https://"):
            url = "https://" + url
        if not re.match("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", url):
            await ctx.send(f"Invalid URL: {url}")

        start = datetime.datetime.utcnow()
        async with self.bot.session.get(url) as resp:
            status = resp.status
        end = datetime.datetime.utcnow()

        elapsed = end - start
        embed = discord.Embed(
            description=f"Request took **{round((elapsed.total_seconds() * 1000), 2)}ms** to complete"
        )
        embed.set_footer(text=f"Status Code: {status}")
        await ctx.send(embed=embed)

    @commands.command(
        aliases=["t"],
    )
    async def timing(self, ctx, time=10):
        """Test your timing!

        As soon as the message shows, click on the reaction after some amount of seconds, by default 10
        Maximum time is 60 seconds and minimum time is 1 second"""
        # Maximum time is 60 seconds and minimum time is 1 second
        time = max(min(time, 60), 1)

        embed = discord.Embed(
            title=f"Try to react to this message with :white_check_mark: exactly after {time} seconds"
        )
        message = await ctx.send(embed=embed)
        await message.add_reaction("\u2705")

        def check(reaction, user):
            return (
                user.id == ctx.author.id
                and reaction.message.channel.id == ctx.channel.id
                and str(reaction.emoji) == "\u2705"
            )

        try:
            # The timeout is one and a half times more than the time
            await self.bot.wait_for("reaction_add", check=check, timeout=time * 1.5)
        except asyncio.TimeoutError:
            return await message.edit(
                embed=discord.Embed(title=f"{ctx.author}, you didn't react with a :white_check_mark:")
            )
        else:
            delay = round((datetime.datetime.utcnow() - message.created_at).total_seconds() - self.bot.latency, 2)
            embed = discord.Embed(title=f"You reacted to this message with :white_check_mark: after {delay} seconds")
            embed.set_footer(text=f"Exact time is {(datetime.datetime.utcnow() - message.created_at).total_seconds()}")
            await message.edit(embed=embed)


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Miscellaneous(bot))

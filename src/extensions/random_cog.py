import random
from collections import Counter
from typing import Optional

import discord
from discord.ext import commands


class Plural:
    """Converts a text to plural when used in a f string

    Examples
    --------
    >>> f"{Plural(1):time}"
    '1 time'
    >>> f"{Plural(5):time}"
    '5 times'
    >>> f"{Plural(1):match|es}"
    '1 match'
    >>> f"{Plural(5):match|es}"
    '5 matches'
    """

    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(v) != 1:
            return f"{v} {plural}"
        return f"{v} {singular}"


class Random(commands.Cog):
    """Random commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(daliases=["cbo"])
    async def choosebestof(self, ctx, times: Optional[int], *choices: commands.clean_content):
        """Chooses between multiple choices N times."""
        if len(choices) < 2:
            return await ctx.send("Not enough choices to pick from.")

        if times is None:
            times = (len(choices) ** 2) + 1

        # The times can be a minimum of 1 and a maximum of 10000
        times = min(10001, max(1, times))
        results = Counter(random.choice(choices) for i in range(times))
        builder = []
        if len(results) > 10:
            builder.append("Only showing top 10 results...")
        for index, (elem, count) in enumerate(results.most_common(10), start=1):
            builder.append(f"{index}. {elem} ({Plural(count):time}, {count / times:.2%})")

        await ctx.send("\n".join(builder))

    @commands.command(
        name="8ball",
        aliases=["eightball", "eight ball", "question", "answer", "8b"],
    )
    async def _8ball(self, ctx, *, question: commands.clean_content):
        """The user asks a yes-no question to the ball, then the bot reveals an answer."""
        answers = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes - definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes Signs point to yes",
            "Reply hazy",
            "try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful",
        ]
        await ctx.send(f"`Question:` {question}\n`Answer:` {random.choice(answers)}")

    @commands.command(aliases=["pick", "choice", "ch"])
    async def choose(self, ctx, *, choices):
        """Chooses a random item from a list of items."""
        # We split it by comma and a comma followed by a space
        choices = choices.split(", ").split(",")
        # We generate the embed
        embed = discord.Embed(
            title="Chosen", description=f"__Choices__: {', '.join(choices)}\n__Chosen__: {random.choice(choices)}"
        )
        # We send the embed
        await ctx.send(embed=embed)

    @commands.command(aliases=["rcmd"])
    async def randomcommand(self, ctx):
        """Sends a random command for you to try"""
        await ctx.send_help(random.choice(list(self.bot.commands)))


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Random(bot))

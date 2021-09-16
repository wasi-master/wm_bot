import asyncio
import os
import random
import re
import string

import discord
from discord.ext import commands

from utils.functions import read_file


class MadLibs(commands.Cog):
    """The classic [madlibs game](https://en.wikipedia.org/wiki/Mad_Libs)"""

    def __init__(self, bot):
        self.bot = bot

        # Setup our regex
        self.regex = re.compile(r"\[\[[^\[\]]+\]\]")

    @commands.command()
    async def madlibs(self, ctx):
        """Let's play MadLibs!"""

        # Check if our folder exists
        if not os.path.isdir("assets/madlibs"):
            return await ctx.channel.send("I'm not configured for MadLibs yet...")

        # Folder exists - let's see if it has any files
        choices = []
        for file in os.listdir("assets/madlibs/"):
            if file.endswith(".txt"):
                choices.append(file)

        if not choices:
            # No madlibs files
            return await ctx.channel.send("No madlibs files found, ask the owner to add one")

        # We have the file, lets notify the user
        await ctx.send("Okay a madlibs game started, reply with `!stop` to stop")

        # Get a random madlib from those available
        random_madlib = random.choice(choices)

        # Let's load our madlibs file
        data = read_file(f"assets/madlibs/{random_madlib}")

        # Set up an empty array of words
        words = []

        # Find all the words that need to be added
        matches = re.finditer(self.regex, data)

        # Get all the words from the matched and add them to a list
        for match in matches:
            words.append(match.group(0))

        # Create empty substitution array
        subs = []

        # Iterate words and ask for input
        for i, word in enumerate(words):
            # We define the vowels
            vowels = "aeiou"
            # The [2:-2] is there to remove the first [[ and the last ]] used by our syntax
            word = word[2:-2]

            # If the word starts with a vowel then we use an instead of a
            is_vowel = word[0].lower() in vowels
            await ctx.channel.send(f"I need a{'n' if is_vowel else ''} **{word}** (word *{i + 1}/{len(words)}*).")

            # Setup the check
            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            # We wait for a response
            try:
                talk = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send("You did not respond")

            # Check if the message is to leave
            if talk.content.lower().startswith(("stop madlibs", "!stop", "!cancel")):
                if talk.author is ctx.author:
                    return await ctx.channel.send(f"Alright, *{ctx.author.name}*.  We'll play another time.")

            # We got a relevant message
            word = talk.content

            # Check for capitalization
            if not word.istitle():
                # Make it properly capitalized
                word = string.capwords(word)

            # Add to our list
            subs.append(word)

        # We replace the placeholders with the words picked by our user
        for asub in subs:
            # Only replace the first occurrence
            data = re.sub(self.regex, f"**{asub}**", data, 1)

        # Send the result
        await ctx.channel.send(data)


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(MadLibs(bot))

import asyncio
import datetime
import json
import random
import unicodedata
from typing import Union

import discord
from attrdict import AttrDict
from discord.ext import commands
from utils.functions import (
    closest_smaller,
    compare_date,
    get_country_emoji,
    get_random_color,
    read_file,
    split_by_slice,
)
from utils.paginator import Paginator


class Fun(commands.Cog):
    """Fun commands :)"""

    def __init__(self, bot):
        self.bot = bot
        self.rickroll = read_file("assets/data/rickroll.txt")

    @commands.command(
        aliases=["randomuser", "randomdude", "randomperson", "ruser", "rdude", "rperson", "randomidentity"]
    )
    async def random_identity(self, ctx, results: int = 1):
        """Sends all details about a randomly generated person that does not exist."""
        async with self.bot.session.get(f"https://randomuser.me/api", params={"results":results}) as r:
            # We wrap the results inside a Attrdict to make it easier to access nested data
            resp = AttrDict(await r.json())
        # We use a list to store the embeds and pass them to the paginator
        embeds = []
        for item in resp.results:
            embed = discord.Embed(
                title=f"{item.name.title}. {item.name.first} {item.name.last}",
                color=0x2CB4FF if item.gender == "male" else 0xFF2CB4,
            )
            embed.set_thumbnail(url=item.picture.large)
            embed.add_field(
                name="Location",
                value=(
                    "```yaml\n"
                    f"{item.location.street.number}, {item.location.street.name}\n"
                    f"City: {item.location.city}\n"
                    f"State: {item.location.state}\n"
                    f"Country: {item.location.country}\n"
                    f"Postal: {item.location.postcode}\n"
                    f"Latitude: {item.location.coordinates.latitude}\n"
                    f"Longitude: {item.location.coordinates.longitude}\n\n"
                    f"```"
                    f"Time Zone\n"
                    f"```yaml\n"
                    f"Offset: {item.location.timezone.offset}\n"
                    f"Description: {item.location.timezone.description}"
                    "```"
                ),
                inline=False,
            )
            embed.add_field(name="Email", value=item.email, inline=False)
            embed.add_field(name="Phone", value=item.phone)
            embed.add_field(name="Cell", value=item.cell)
            embed.add_field(
                name="Picture",
                value=(
                    f"[Large 128x128]({item.picture.large})\n"
                    f"[Medium 64x64]({item.picture.medium})\n"
                    f"[Small 48x48]({item.picture.thumbnail})"
                ),
            )
            embed.add_field(
                name="Login",
                value=(
                    "```yaml\n"
                    f"UUID: {item.login.uuid}\n"
                    f"Username: {item.login.username}\n"
                    f"Password: {item.login.password}\n"
                    f"Salt: {item.login.salt}\n"
                    f"MD5: {item.login.md5}\n"
                    f"SHA1: {item.login.sha1}\n"
                    f"SHA256: {item.login.sha256}"
                    "```"
                ),
                inline=False,
            )
            embed.add_field(name="Nationality", value=get_country_emoji(item.nat))
            embeds.append(embed)
        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @commands.command(aliases=["co"])
    async def cookie(self, ctx):
        """Who can catch the cookie first?"""

        # We send cookie is coming and then wait for 3 seconds
        m = await ctx.send(embed=discord.Embed(title="🍪 Cookie is coming..."))
        await asyncio.sleep(3)

        # Now every second we edit the message till the time is 0
        for i in range(3, 0, -1):
            await m.edit(embed=discord.Embed(title=f"🍪 Cookie is coming in **{i}**"))
            await asyncio.sleep(1)

        # If the time is 0 then we start the challenge
        # First we save the start time
        start = datetime.datetime.utcnow()
        await m.add_reaction("🍪")
        try:
            # Now we wait for the reaction
            _, user = await self.bot.wait_for(
                "reaction_add",  # an reaction is being added
                check=lambda r, u: str(r.emoji) == "🍪"  # the emoji is cookie
                and r.message == m  # the reaction is on the message we want
                and not u.bot,  # the reaction was not by a bot
                timeout=10,  # we stop after 10 seconds
            )
        except asyncio.TimeoutError:
            await ctx.send("No one got the cookie :(")
        else:
            time = round((datetime.datetime.utcnow() - start).total_seconds() - self.bot.latency, 3)
            await m.edit(embed=discord.Embed(title=f"**{user.display_name}** got the cookie in **{time}** seconds"))

    @commands.command(aliases=["giveyouup", "gyu", "nggyu", "never_gonna_give_you_up", "rickroll"])
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def nevergonnagiveyouup(self, ctx, whotogiveup: Union[discord.Member, str]):
        """Textual rickroll, sends the rickroll lyrics with the name being the person specified"""
        person = whotogiveup.display_name if isinstance(whotogiveup, discord.Member) else whotogiveup

        # We don't want people spamming
        if len(person) > 2:
            return await ctx.send("Why so large name? not gonna do that")

        # We format the text
        rickroll_text = self.rickroll.format(person)
        rickroll_text = discord.utils.escape_markdown(rickroll_text)

        # We send the actual rickroll
        await ctx.send(rickroll_text, allowed_mentions=discord.AllowedMentions.none())

    @commands.command()
    @commands.guild_only()
    async def snipe(self, ctx, channel: discord.TextChannel = None):
        """Sends the last deleted message in the channel, can be unavailable"""
        # We get the info
        channel = channel or ctx.channel
        snipes = self.bot.snipes

        # If there isn't any sniped messages we notify the user
        if not snipes.get(channel.id):
            return await ctx.send("No messages to snipe")

        # We get the info
        message = snipes[channel.id]
        author = message.author

        # We make the embed
        embed = discord.Embed(
            title="Said:",
            description=message.content,
            timestamp=message.created_at,
            color=discord.Colour.green(),
        )
        # We set the thumbnail
        embed.set_thumbnail(url=author.avatar.url)
        # We set the name
        name = f"{author} ({author.display_name})" if author.nick else author.name
        embed.set_author(icon_url=author.avatar.url, name=name)
        # We send the message
        await ctx.send(embed=embed)

    @commands.command()
    async def imagine(self, ctx, *, thing):
        """Tells you if the bot can imagine the thing"""
        chance = random.random()
        if chance < 0.80:
            await ctx.send(f"I can't even imagine {thing} bro")
        else:
            await ctx.send(f"{thing} is good bro")

    @commands.command()
    @commands.guild_only()
    async def cakeday(self, ctx):
        """Shows the people who has their discord birthday today, inspired by reddit"""
        # We get the current time
        current = datetime.datetime.utcnow()
        # We get the people that created their account on this day
        people = []

        # We add the people that have created their account on this day to a list
        # I know this can be shortened into a list comprehension but that doesn't look clean
        for i in ctx.guild.members:
            if compare_date(i.created_at.date(), current.date()):
                people.append(i)

        # We paginate
        embeds = []
        for chunk in split_by_slice(people, length=5):
            # We make a embed with a random color
            embed = discord.Embed(color=get_random_color())
            for member in chunk:
                # We add the member to the embed
                age = current.year - member.created_at.year
                embed.add_field(
                    name=member.display_name,
                    value=f"Person: {member.mention}"
                    f"Created At: {discord.utils.format_dt(member.created_at, 'F')}\n"
                    f"Age: {age} Year{'s' if age > 1 else ''}",
                    inline=False,
                )
            embeds.append(embed)

        if not embeds:
            return await ctx.send("No one created their account on this day")

        # We start the pagination
        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @commands.command()
    async def advice(self, ctx):
        """Gives a random advice"""
        async with self.bot.session.get("https://api.adviceslip.com/advice") as r:
            resp = json.loads(await r.text())
            await ctx.send(embed=discord.Embed(title="Advice", description=resp["slip"]["advice"], color=0x2F3136))

    @commands.command()
    async def topic(self, ctx):
        """Gives a random topic to discuss"""
        async with self.bot.session.get("https://dinosaur.ml/random/topic/") as r:
            resp = await r.json()
            await ctx.send(discord.Embed(title="Topic", description=resp["topic"], color=0x2F3136))

    @commands.command(aliases=["bsm", "bsmap", "map"])
    @commands.cooldown(1, 2, commands.BucketType.default)
    async def brawlstarsmap(self, ctx, *, provided_map: str):
        embed = discord.Embed()
        maplist = provided_map.split(" ")
        map = ""
        for i in maplist:
            preps = ["on", "the", "of"]
            if not i.strip().lower() in preps:
                map += " " + i.lower().capitalize()
            else:
                map += " " + i.lower()
        map = map.strip().replace(" ", "-")
        url = f"https://www.starlist.pro/assets/map/{map}.png"
        # session = aiohttp.ClientSession()
        async with self.bot.session.get(url) as response:
            text = await response.text()
            if "Not Found" in text:
                embed.add_field(
                    name="Map not found",
                    value=f"The map `{map.replace('-', ' ')}` is not found",
                )
            else:
                embed.set_image(url=url)
        embed.title = map.replace("-", " ")
        await ctx.send(embed=embed)

    @commands.command()
    async def groot(self, ctx):
        """Who... who are you?"""
        groots = [
            "I am Groot",
            "**I AM GROOT**",
            "I... am... *Groot*",
            "I am Grooooot",
            "i am groot",
        ]
        punct = [
            "!",
            ".",
            "?",
        ]
        # Build our groots
        groot = " ".join([random.choice(groots) + (random.choice(punct) * random.randint(0, 5))])
        await ctx.send(groot)

    # @commands.command(
    #     aliases=["q", "triv", " trivia"], description="Sends a quiz for you to answer"
    # )
    # async def quiz(self, ctx):
    # TODO: re implement

    @commands.command(
        aliases=["hg", "howlesbian", "hl"],
    )
    @commands.guild_only()
    async def howgay(self, ctx, member: discord.Member = None):
        """Shows how gay a person is (random)"""
        member = member or ctx.author
        male = ctx.invoked_with in ("hg", "howgay")

        gay = random.randint(0, 100) if ctx.author.id != self.bot.owner_id else 0

        embed = discord.Embed(colour=member.color)
        embed.set_author(name=f"{'Gay' if male else 'Lesbian'} Telling Machine")
        embed.set_footer(text=f"Requested by {ctx.author}")
        embed.add_field(
            name=f"How {'Gay' if male else 'Lesbian'}?", value=f"{member.name} is {gay}% {'Gay' if male else 'Lesbian'}"
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["mem"])
    async def meme(self, ctx):
        """Sends a random meme"""
        # I know I can use the reddit api but I did this like a long time ago and I am too lazy to fix it
        async with self.bot.session.get("https://meme-api.herokuapp.com/gimme") as r:
            fj = json.loads(await r.text())
        embed = discord.Embed(title=fj["title"], url=fj["postLink"], color=0xFF5700)
        embed.set_image(url=fj["url"])
        await ctx.send(embed=embed)

    @commands.command(aliases=["rps"])
    @commands.guild_only()
    async def rockpaperscissors(self, ctx):
        """Play the classic rock paper scissors game"""

        await ctx.send("Type `rock` or `paper` or `scissors`")

        def check(message):
            return (
                message.author == ctx.author
                and message.channel == ctx.channel
                and message.content in ["rock", "paper", "scissors"]
            )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=15)
        except asyncio.TimeoutError:
            return await ctx.reply("Didn't respond with neither `rock`, `paper` or `scissors`")
        else:
            user_action = msg.content.lower()
            computer_action = random.choice(["rock", "paper", "scissors"])

            if user_action == computer_action:
                await msg.reply(f"I picked {computer_action}, Both players selected `{user_action}`. It's a tie!")

            elif user_action == "rock":
                if computer_action == "scissors":
                    await msg.reply(f"I picked {computer_action}, Rock smashes scissors! You win!")
                else:
                    await msg.reply(f"I picked {computer_action}, Paper covers rock! You lose.")

            elif user_action == "paper":
                if computer_action == "rock":
                    await msg.reply(f"I picked {computer_action}, Paper covers rock! You win!")
                else:
                    await msg.reply(f"I picked {computer_action}, Scissors cuts paper! You lose.")

            elif user_action == "scissors":
                if computer_action == "paper":
                    await msg.reply(f"I picked {computer_action}, Scissors cuts paper! You win!")
                else:
                    await msg.reply(f"I picked {computer_action}, Rock smashes scissors! You lose.")

    @commands.command(name="chatbot", aliases=["cb"])
    async def chatbot(self, ctx):
        """Talk to AI Chatbot"""

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        embed = discord.Embed(
            title="Session has started",
            description="Say anything you like and chatbot will respond, may take up to 5 seconds for it to respond, say `cancel` to cancel",
        )
        embed.set_footer(text="Timeout in 60 secs")
        await ctx.send(embed=embed)
        while True:
            try:
                msg = await self.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                await ctx.reply("What about the chatbot, you didn't respond")
                return
            if "cancel " in msg.content.lower():
                await msg.reply("Okay, stopped")
                break

            response = await self.bot.cleverbot.ask(msg.content, msg.author.id)
            embed = discord.Embed(title="AI Responded", description=response.text)
            embed.set_footer(text="Timeout in 60 secs")
            await msg.reply(embed=embed)

    @commands.command(aliases=["pp", "ppsize"])
    @commands.guild_only()
    async def penis(self, ctx, *, member: discord.Member = None):
        """See someone's penis size (random)"""
        member = member or ctx.author
        ppsize = random.randint(0, 30)
        sizedict = {
            0: "hehe, pp smol",
            6: "okay",
            10: "normal pp",
            13: "huge pp",
            19: "extremely big pp",
            26: "tremendous pp",
        }
        comment = closest_smaller(sizedict, ppsize)

        embed = discord.Embed(
            title=f"{member.name}'s pp size",
            description=f'8{"=" * ppsize}D',
            color=0x2F3136,
        )
        embed.set_footer(text=comment)
        await ctx.send(embed=embed)

    @commands.command()
    async def emojiparty(self, ctx):
        """The bot will send the name of every emoji reacted to the bot's message"""
        message = await ctx.send("React to this message with any emoji")
        emoji_list = []

        def check(reaction, _):
            return reaction.message.channel.id == ctx.channel.id and reaction.message.id == message.id

        while True:
            try:
                reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=15)
            except asyncio.TimeoutError:
                await message.edit(content=message.content + "\n\nOkay I stopped now :)")
                return
            else:
                if isinstance(reaction.emoji, (discord.Emoji, discord.PartialEmoji)):
                    emoji_list.append(f"{reaction.emoji} - {reaction.emoji.name}")
                    await message.edit(content="\n".join(emoji_list))
                else:
                    emoji_list.append(f"{reaction.emoji} - {reaction.emoji.name}")
                    await message.edit(content="\n".join(emoji_list))
                    try:
                        emoji_list.append(f"{reaction.emoji} - {unicodedata.name(reaction.emoji).title()}")
                        await message.edit(content="\n".join(emoji_list))
                    except Exception:
                        try:
                            await message.remove_reaction(reaction.emoji, ctx.author)
                        except discord.Forbidden:
                            pass

    # TODO: fix
    # @commands.command(aliases=["wtp","gtp","guessthepokemon"])
    # async def whatsthispokemon(self, ctx):
    #     """Guess the pokemon"""

    #     headers = {"token": token_ommited}

    #     def check(m):
    #         return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

    #     async with self.bot.session.get("https://dagpi.tk/api/wtp", headers=headers) as cs:
    #         fj = await cs.json()
    #     embed = discord.Embed(title="What's this pokemon?")
    #     embed.set_image(url=fj["question_image"])
    #     await ctx.send(embed=embed)
    #     counter = 0
    #     max_tries = 3
    #     guessed = 0
    #     while True:
    #         try:
    #             message = await self.bot.wait_for("message", check=check, timeout=20)
    #             if message.content.lower() == fj["pokemon"]["name"].lower():
    #                 embed = discord.Embed(
    #                     title="You got it right",
    #                     description=f"The pokemon was {fj['pokemon']['name']}",
    #                 )
    #                 embed.set_image(url=fj["answer_image"])
    #                 await ctx.send(embed=embed)
    #                 return
    #             elif message.content.lower() == "hint":
    #                 guessed += 1
    #                 counter += 1
    #                 if counter == 1:
    #                     await ctx.send("You can't get a hint without guessing")
    #                 elif counter > 1:
    #                     name = list(fj["pokemon"]["name"])
    #                     for index, i in enumerate(name):
    #                         if random.randint(0, 100) >= 40:
    #                             name[index] = "_"
    #                     name = "".join(name)
    #                     await ctx.send(f"The pokemon name is {name}")
    #             else:
    #                 await ctx.send(f"Wrong.send( you have {max_tries - counter} tries left")
    #                 if counter >= 1:
    #                     await ctx.send(f"Wrong.send( you can try `hint` to get a hint")
    #                 elif counter == max_tries:
    #                     embed = discord.Embed(
    #                         title="You lost",
    #                         description="The pokemon was {fj['pokemon']['name']}",
    #                     )
    #                     embed.set_image(url=fj["answer_image"])
    #                     await ctx.send(embed=embed)
    #                     return
    #         except asyncio.TimeoutError:
    #             await ctx.send(f"{ctx.author.mention}.send( you didn't reply within time")
    #             return


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Fun(bot))

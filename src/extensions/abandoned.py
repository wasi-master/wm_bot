@commands.command(aliases=["synonym"], description="Sends synomyms for a word")
async def synonyms(self, ctx, *, word):
    api_key = "dict.1.1.20200701T101603Z.fe245cbae2db542c.ecb6e35d1120ee008541b7c1f962a6d964df61dd"

    async with ctx.typing():
        embed = discord.Embed(timestamp=ctx.message.created_at)
        embed.set_author(name=f"Synonyms for {word}")
        async with self.bot.session.get(
            f"https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key={api_key}&lang=en-en&text={word.lower()}"
        ) as response:
            data = await response.json()

        num = 0
        try:
            synonyms = data.get("def")[0].get("tr")
            for i in synonyms:
                num += 1
                embed.add_field(name=f"Synonym {num}", value=i.get("text"), inline=True)
        except:
            embed.add_field(name="No synonyms found", value="‌Command Aborted")
    await ctx.send(embed=embed)



# Games cog
import asyncio
import json
import random
from collections import Counter

import discord
from discord.ext import commands


class Games(commands.Cog):
    """Game Releated commands (most games have their own separate cog)"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["gtn"])
    @commands.has_permissions(manage_messages=True)
    async def guessthenumber(self, ctx, number_range: str):
        if len(number_range.split("-")) == 1 and number_range.isdigit():
            start_range = 1
            end_range = int(number_range.strip())
        elif len(number_range.split("-")) == 2:
            start_range, end_range = [int(i.strip()) for i in number_range.split("-")]
        else:
            await ctx.send("Invalid range")
            return
        if not end_range > start_range:
            await ctx.send("End is smaller than start")
            return
        # start_range, end_range = abs(start_range), abs(end_range)
        num = random.randint(start_range, end_range)
        perms = ctx.channel.overwrites_for(ctx.guild.default_role)
        if not perms.send_messages:
            perms.send_messages = True
            try:
                await ctx.channel.edit(overwrites={ctx.guild.default_role: perms})
            except discord.Forbidden:
                await ctx.send("Send messages permission for \@everyone is denied")
        await ctx.send(f"Okay, I picked a number between {start_range} and {end_range}, now try to guess what it is")
        await ctx.author.send(f"The number is ||{num}||\n\nDon't click on the spoiler if you want to participate")
        allowed_words = ["end", "stop", "cancel", "hint", "h"]
        tries = 0
        last_hint = 0
        users = []
        while True:
            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.channel == ctx.channel and not m.author.bot,
                    timeout=900,
                )
                if msg.content.isdigit():
                    guess = int(msg.content)
                    if guess > end_range:
                        await msg.delete()
                        await msg.author.send(
                            f"You sent {guess} which is higher than the highest number possible (**{end_range}**)"
                        )
                    elif guess < start_range:
                        await msg.delete()
                        await msg.author.send(
                            f"You sent {guess} which is lower than the smallest number possible (**{start_range}**)"
                        )
                    if guess == num:
                        try:
                            perms.send_messages = False
                            await ctx.channel.edit(overwrites={ctx.guild.default_role: perms})
                        except discord.Forbidden:
                            pass

                        await msg.pin(reason="Won the guess the number game")
                        await ctx.send(":partying_face::partying_face::partying_face::partying_face::partying_face:")
                        embed = discord.Embed(
                            title=f":partying_face: {msg.author.name} Won the game",
                            description=f":tada: Congrats, {msg.author.name}, the number was {num}",
                            color=discord.Colour.green(),
                        )
                        d = dict(Counter(users))
                        parti = "\n".join([f"{ctx.guild.get_member(id).display_name} - {d[id]}" for id in d])
                        embed.add_field(name="Tries", value=parti)
                        embed.add_field(name="Total Tries", value=str(tries))
                        await ctx.send(msg.author.mention.send(embed=embed))
                        return
                    else:
                        tries += 1
                        users.append(msg.author.id)
                else:
                    if msg.content in allowed_words:
                        # if (not msg.author.permissions_in(ctx.channel).manage_guild) and (not msg.content in ("hint", "h"))
                        # await ctx.send(f"{msg.author.mention}.send(lYou can\'t do that")
                        if msg.content in ("stop", "end", "cancel"):
                            if msg.author.permissions_in(ctx.channel).manage_guild:
                                await ctx.send("Okay stopped the guessing game :(")
                                return
                            else:
                                await ctx.send(
                                    f"{msg.author.mention}, You don't have the permissions required to stop the guessing game"
                                )
                        elif msg.content in ("hint", "h"):
                            if last_hint == 0:
                                last_hint = tries
                            if not (tries - last_hint) < 3:
                                hint_num = random.randint(1, 2)
                                if hint_num == 1:
                                    if len(str(start_range)) != len(str(end_range)):
                                        await ctx.send(f"The number has {len(str(num))} digits")
                                elif hint_num == 2:
                                    digits = len(str(num))
                                    digit = random.randint(0, digits)
                                    picked_digit = str(num)[digit]
                                    nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
                                    nums = random.sample(nums, 9)
                                    nums.append(digit)
                                    nums = [str(i) for i in set(nums)]
                                    ordinal = lambda n: "%d%s" % (
                                        n,
                                        "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4],
                                    )
                                    await ctx.send(
                                        f"The {ordinal(digit+1)} digit of the picked number is in `{', '.join(nums)}`"
                                    )
                                else:
                                    await ctx.send(
                                        f"{msg.author.mention}, Can't get a hint yet, try guessing some more"
                                    )

                    else:
                        await msg.delete()
                        await msg.author.send("**you're only allowed to send numbers** there")
            except asyncio.TimeoutError:
                await ctx.send(
                    embed=discord.Embed(
                        color=discord.Colour.red(),
                        title="Guess The Number Timed out",
                        description=f"No one sent a message in thr last 15 minutes so I assume everyone left the game\n\nThe number was {num}",
                    )
                )
                return

    @commands.command(aliases=["tod"], description="Truth Or Dare")
    async def truthordare(self, ctx, questype: str = "random"):
        levels = ["Disgusting", "Stupid", "Normal", "Soft", "Sexy", "Hot"]

        async with self.bot.session.get(
            "https://raw.githubusercontent.com/sylhare/Truth-or-Dare/master/src/output.json"
        ) as r:
            fj = json.loads(await r.text())

        if questype == "random":
            number = random.randint(0, 553)
            picked = fj[number]
            level = levels[int(picked["level"])]
            summary = picked["summary"]
            questiontype = picked["type"]
        else:
            return
        embed = discord.Embed(color=0x2F3136)
        embed.set_author(name=summary)
        embed.add_field(name="Level", value=level)
        embed.add_field(name="Type", value=questiontype)
        await ctx.send(embed=embed)


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Games(bot))



    @commands.command(aliases=["fe", "fi"])
    @commands.cooldown(1, 10, BucketType.user)
    async def fileinfo(self, ctx, file_extension: str):
        """Shows info about a file extension"""
        msg = await ctx.send(f"Searching {self.bot.emoji_config.loading.typing}")
        async with self.bot.session.get(f"https://fileinfo.com/extension/{file_extension}") as resp:
            data = await resp.text()
        await msg.edit(content=f"Loading {self.bot.get_custom_emoji('load.typing')}")
        soup = BeautifulSoup(data, "lxml")

        filename = soup.find_all("h2")[0].get_text().replace("File Type", "")

        developer = soup.find_all("table")[0].find_all("td")[1].get_text()

        fileType = soup.find_all("a")[10].get_text()

        fileFormat = soup.find_all("a")[11].get_text()

        whatIsIt = soup.find_all("p")[0].get_text()

        moreInfo = soup.find_all("p")[1].get_text()

        embed = discord.Embed(title=filename, description=whatIsIt)
        if developer != "N/A" and len(developer) != 0:
            embed.add_field(name="Developed by", value=developer)
        if fileType != "N/A" and len(fileType) != 0:
            embed.add_field(name="File Type", value=fileType)
        if fileFormat != "N/A" and len(fileFormat) != 0:
            embed.add_field(name="File Format", value=fileFormat)
        if moreInfo != "N/A" and len(moreInfo) != 0:
            embed.add_field(name="More Info", value=moreInfo)
        await ctx.send(embed=embed)
        await msg.delete()



@commands.group(aliases=["dl"], invoke_without_command=False)
@commands.cooldown(1, 15, BucketType.user)
async def download(self, ctx):
    pass

@download.command(name="mpeg4", aliases=["mp4"])
@commands.cooldown(1, 15, BucketType.user)
async def download_mpeg4(self, ctx, url):
    yt = YouTube(url)
    embed = discord.Embed()
    desc = "__Found these formats, which one do you want to download? type the number__\n\n"
    get_streams_func = functools.partial(get_streams, yt, file_extension="mp4")
    streams = await self.bot.loop.run_in_executor(None, get_streams_func)
    streamed_items = [i[1] for i in streams]
    for num, stream in enumerate(streamed_items, 1):
        if stream.type == "audio":
            continue
        desc += f"**{num}.**\nFile Extension: `.{stream.mime_type.replace('video/', '')}`\nResolution{stream.resolution}@{stream.fps}\nFile Size: {humanize.naturalsize(stream.filesize, False, True)}\n"
    embed.description = desc
    await ctx.send(embed=embed)
    try:
        msg = await self.bot.wait_for(
            "message",
            check=lambda msg: msg.author == ctx.author
            and msg.channel == ctx.channel,
            timeout=60,
        )
    except asyncio.TimeoutError:
        return await ctx.reply("Welp, You didn't respond")
    else:
        if not msg.content.isnumeric():
            return
        try:
            stream = streamed_items[int(msg.content) - 1]
            filesize = stream.filesize
            await ctx.send(
                embed=discord.Embed(
                    title="Download Video",
                    description=f"[Click Here]({stream.url}) to download the video. \n Note: the video is `{humanize.naturalsize(stream.filesize, False, True)}`",
                )
            )
        except IndexError:
            return await msg.reply("That number wasn't in the list smh")


# Telephone
import asyncio
import random
import typing

import discord
from discord.ext import commands

from utils.converters import TelephoneConverter
from utils.functions import get_agreement


class Telephone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["call", "tp"], invoke_without_command=True)
    async def telephone(self, ctx, person: typing.Union[discord.Member, TelephoneConverter]):
        phone_number = await self.bot.db.fetchrow(
            """
            SELECT phone_number FROM telephones WHERE user_id = $1
            """,
            ctx.author.id,
        )
        if phone_number is None:
            return await ctx.send(f"You don't have a phone number, create one with `{ctx.prefix}telephone rgister`")
        if isinstance(person, TelephoneConverter):
            user_id = await self.bot.db.fetchrow(
                """
                SELECT user_id FROM telephones WHERE phone_number = $1
                """,
                person,
            )
            phone_number = person
            if user_id is None:
                return await ctx.send("No one has that telephone number.")
            user = self.bot.get_user(user_id)
        elif isinstance(person, discord.Member):
            phone_number = await self.bot.db.fetchrow(
                """
                SELECT phone_number FROM telephones WHERE user_id = $1
                """,
                person.id,
            )
            user = person
            if phone_number is None:
                return await ctx.send("The person has no telephone number")
        if not await get_agreement(
            ctx,
            f"{ctx.author} is calling you. do you accept it?",
            user.dm_channel,
            user,
            300,
        ):
            return await ctx.reply(f"{user.name} Declined the call")

        def check(msg):
            return msg.author in (ctx.author, user) and msg.channel in (
                ctx.channel,
                ctx.author.dm_channel,
                user.dm_channel,
            )

        await ctx.reply(
            f"You have started a call with {user.name}, write anything here and it'll be sent to the user. type `wm,cancel` to cancel"
        )
        await user.send(
            f"Call started with {ctx.author.name}, write anything here and it'll be sent to the user. type `wm,cancel` to cancel"
        )
        while True:
            try:
                message = await self.bot.wait_for("message", check=check, timeout=120)
                if message.author == ctx.author:
                    await user.send(f"**__{ctx.author.name}__**: {message.content}")
                if message.author == user:
                    await ctx.send(f"**__{user.name}__**: {message.content}")
                if message.content.startswith("wm,cancel"):
                    if message.author == ctx.author:
                        await ctx.send("You have cancelled the call")
                        await user.send(f"{ctx.author.name} has cancelled the call")
                        return
                    if message.author == user:
                        await user.send("You have cancelled the call")
                        await ctx.reply(f"{user.name} has cancelled the call")
                        return

            except asyncio.TimeoutError:
                await user.send("Timed out")
                await ctx.reply("Timed out")
                return

    @telephone.command(name="register", aliases=["new", "create", "n", "r", "c"])
    async def telephone_register(self, ctx):
        phone_number = await self.bot.db.fetchrow(
            """
            SELECT phone_number FROM telephones WHERE user_id = $1
            """,
            ctx.author.id,
        )
        if phone_number:
            if not await get_agreement(ctx, "You already have a telephone, do you want to create a new number?"):
                return
        phone_number = int("".join(str(random.randint(0, 9)) for i in range(11)))
        await self.bot.db.execute(
            """
                INSERT INTO telephones (user_id, phone_number)
                VALUES ($1, $2)
                """,
            ctx.author.id,
            phone_number,
        )
        await ctx.send(
            embed=discord.Embed(
                title="Registration Succesfull",
                color=discord.Color.green(),
                description=f"Your phone number is {phone_number}",
            )
        )


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Telephone(bot))


# @commands.command(aliases=["copyguild", "servercopy", "guildcopy"])
# # @bot_has_permissions()
# async def copyserver(self, ctx, copy_to: int):
#     if (guild := self.bot.get_guild(copy_to)):
#         if not ctx.author in guild.members:
#             return await ctx.send("You are not in that server")
#         if ctx.author.id != guild.owner_id:
#             return await ctx.send("You are in that server but you do not own that server")
#         if ctx.author.id != ctx.guild.owner_id:
#             return await ctx.send("You do own that server but do not own this server")
#         m = await ctx.send("Work Starting")
#         await asyncio.sleep(3)
#         await m.edit(content="Deleting all channels of that server")
#         for channel in guild.channels:
#             await channel.delete(reason=f"Copying From {ctx.guild.name} (ID: {ctx.guild.id})")
#         await m.edit(content="Creating all channels from this server to that server")
#         missed = {}
#         for channel in ctx.guild.channels:
#             if isinstance(channel, discord.TextChannel):
#                 try:
#                     if channel.category is None:
#                         await guild.create_text_channel(name=channel.name, overwrites=overwrites)
#                 except Exception as e:
#                     missed[channel] = str(e)
#             elif isinstance(channel, discord.VoiceChannel):
#                 try:
#                     # TODO: write code...
#                     pass
#                 except Exception as e:
#                     missed[channel] = str(e)
#             elif isinstance(channel, discord.CategoryChannel):
#                 try:
#                     # TODO: write code...
#                     pass
#                 except Exception as e:
#                     missed[channel] = str(e)
#             else:
#                 missed[channel] = "Can't copy this type of channel"
#     else:
#         await ctx.send("The bot is not in that server")


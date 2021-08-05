import asyncio
import base64
import datetime
import json
import os
import random
import shutil
from zipfile import ZipFile

import discord
import humanize
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ext.commands import BucketType
from utils.paginator import Paginator

from utils.functions import get_all_file_paths, get_p


class Utility(commands.Cog):
    """General utilities"""

    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=["redirect", "unshort", "us"])
    async def unshorten(self, ctx, url: str):
        """Got a shortened link? bit.ly? use this command to un shorten the link!

        Does not work for website that do not redirect you to the long url directly.
        """
        async with self.bot.session.get(url, allow_redirects=True) as resp:
            if resp.url == url: # XXX: there may be a better way to do this
                return await ctx.send("The url didn't redirect me to any website :(")
            result_url = resp.url

        embed = discord.Embed(
            title=f"{url} redirected me to",
            description=result_url,
            color=discord.Colour.red(),
        )
        embed.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Command executed by {ctx.author}, to see all redirects use the redirects command",
        )
        await ctx.send(embed=embed)

    @commands.command(name="id", aliases=["snowflake", "snf"])
    async def snowflake(self, ctx, *, snowflake_id: int):
        """Show the date a snowflake ID was created"""
        # Follows https://discord.com/developers/docs/reference#convert-snowflake-to-datetime
        timestamp = ((snowflake_id >> 22) + 1420070400000) / 1000  # python uses seconds not milliseconds
        creation_date = datetime.datetime.utcfromtimestamp(timestamp)
        return await ctx.send(f"ID created {discord.utils.format_dt(creation_date, 'R')}")

    @commands.command(aliases=["snowflakeinfo", "snfi", "idi"])
    async def idinfo(self, ctx, *, snowflake_id: int):
        """Show all available data about a snowflake ID"""
        # Follows https://discord.com/developers/docs/reference#convert-snowflake-to-datetime
        timestamp = ((snowflake_id >> 22) + 1420070400000) / 1000  # python uses seconds not milliseconds
        internal_worker_id = (snowflake_id & 0x3E0000) >> 17
        internal_process_id = (snowflake_id & 0x1F000) >> 12
        internal_counter = snowflake_id & 0xFFF

        creation_date = datetime.datetime.utcfromtimestamp(timestamp)
        formatted_date = creation_date.strftime("%A, %B %d %Y at %H:%M:%S UTC")

        embed = discord.Embed(title=snowflake_id, description="Discord snowflake ID")
        embed.add_field(name="Date created", value=formatted_date, inline=False)
        embed.add_field(name="Internal worker/process", value=f"{internal_worker_id}/{internal_process_id}", inline=False)
        embed.add_field(name="Internal counter", value=internal_counter, inline=False)
        embed.add_field(name="As user ping", value="<@{}>".format(snowflake_id))
        embed.add_field(name="As channel ping", value="<#{}>".format(snowflake_id))
        embed.add_field(name="As role ping", value="<@&{}>".format(snowflake_id))
        embed.add_field(name="As custom emote", value="<:test:{}>".format(snowflake_id))
        embed.add_field(name="As animated emote", value="<a:test:{}>".format(snowflake_id))

        await ctx.send(embed=embed)

    @commands.command(aliases=["pt"])
    async def parsetoken(self, ctx, token):
        """Parses a token and sends who the token is for"""
        user, _, _ = token.split(".")

        user_id = base64.b64decode(user).decode("utf-8")
        user = await self.bot.fetch_user(user_id)

        embed = discord.Embed(title=(user), description=f"ID: `{user.id}`")
        embed.set_thumbnail(url=str(user.avatar.url))
        embed.add_field(name="Type", value="Bot Token" if user.bot else "Account Token")
        embed.add_field(
            name="Account Creation",
            value=f'{discord.utils.format_dt(user.created_at, "F")} ({discord.utils.format_dt(user.created_at, "R")})',
            inline=False,
        )
        # FIXME: this does not work
        # embed.add_field(
        #     name="Token Creation",
        #     value=f'{time.strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.datetime.utcnow() - time)})',
        #     inline=False,
        # )

        await ctx.send(embed=embed)

    @commands.command(aliases=["rd"])
    async def redirects(self, ctx, url: str):
        """Sends all the websites a certain websites redirects to"""
        response = await self.bot.session.get(url)

        embed = discord.Embed(title=url, url=url)
        for num, resp in enumerate(response.history, 1):
            embed.add_field(
                name=f"Redirect {num}",
                value=f"URL: {resp.url}\nCode: {resp.code} ({resp.reason})",
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.command()
    async def embed(self, ctx, *, embed_json):
        # We strip the codeblock formatting if there is any
        embed_json = embed_json.lstrip("```json\n").strip("```").strip()
        try:
            embed_dict = json.loads(embed_json)
        except json.JSONDecodeError as error:
            embed = discord.Embed(
                title="Invalid JSON",
                color=0xFF0000,
                description=f"```json\n{embed_json}```",
            ).set_footer(text=str(error) + " (Invalid JSON)")
            embed.set_footer(text=str(error))

            return await ctx.send(embed=embed)

        # We format the color to be a int since the api accepts only ints
        if (col := embed_dict.get("color", embed_dict.get("colour"))) :
            if isinstance(col, str):
                converter = commands.ColourConverter()
                embed_dict["color"] = (await converter.convert(ctx, col)).value

        try:
            emby = discord.Embed.from_dict(embed_dict)
        except Exception as error:
            return await ctx.send("Error occurred: " + str(error))

        try:
            # If the author does not have the manage messages permission then we specify who sent the embed
            if ctx.author == self.bot.owner or ctx.channel.overwrites_for(ctx.author).manage_messages:
                await ctx.send(embed=emby)
            else:
                await ctx.send(f"Sent by {ctx.author}", embed=emby)
        except Exception as exc:
            if hasattr(exc, "code"):
                exc: discord.HTTPException # to make my linter shut up
                if exc.code == 50006:
                    return await ctx.send("Invalid embed (probably empty)")
                elif exc.code == 50035:
                    return await ctx.send("Invalid Field: " + str(exc))
                else:
                    return await ctx.send("Error Occurred: " + str(exc))
            else:
                return await ctx.send("Error Occurred: " + str(exc))

    @commands.command()
    async def dm(self, ctx, *, message: str = None):
        """Sends you a direct message containing the message specified"""
        if message is None:
            if ctx.message.reference:
                return await ctx.author.send(ctx.message.reference.jump_url)

        await ctx.author.send(message or ctx.message.jump_url)
        await ctx.message.add_reaction(self.bot.emoji_config.validation.green_tick)

    @commands.command(aliases=["members"])
    async def getusers(self, ctx, *, role: discord.Role):
        """Sends the names of all the people in the role specified"""
        if not role.members:
            return await ctx.send("No Members")

        paginator = commands.Paginator(prefix="", suffix="")
        for member in role.members:
            paginator.add_line(f"{member}{f'({member.display_name})' if member.nick else ''}")

        embeds = []
        for page in paginator.pages:
            embeds.append(
                discord.Embed(
                    description=page,
                    color=role.color or 0x2F3136 ,
                )
            )

        menu = Paginator(embeds)
        menu.start(ctx)

    @commands.command()
    async def tos(self, ctx, *, term: str):
        """Searches discord terms of service"""
        # I may remove this in the future
        await ctx.send(f"Go to <https://discord.com/terms>. Press Ctrl+F and write {term}")


    @commands.command()
    async def dice(self, ctx):
        """Rolls a dice and gives you a number ranging from 1 to 6"""
        dice_emoji = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:"]
        dice = random.randint(0, 5)

        msg = await ctx.send(f":game_die: Rolling Dice {self.bot.get_custom_emoji('load.typing')}")
        await asyncio.sleep(2)
        await msg.edit(content=f"Your number is  {dice_emoji[dice]}")

    @commands.command(
        aliases=["ph", "catch"],
    )
    async def pokemonhack(self, ctx, channel: discord.TextChannel = None):
        """Tells you which pokemon it is that has been last spawned by a bot"""
        # FIXME: document this command
        #  msg1 = await ctx.send(f"Finding {self.bot.get_custom_emoji('load.typing')}")
        channel = channel or ctx.channel
        url = None
        img_url = None
        raw_result = None
        async for message in channel.history(limit=8, oldest_first=False, before=ctx.message):
            if message.author != ctx.guild.me:
                if message.embeds:
                    embed = message.embeds[0]
                    if not embed.image:
                        pass
                    else:
                        img_url = embed.image.url
                else:
                    pass
            else:
                pass
        if not img_url:
            return await ctx.send("Message containing a pokemon Not Found")
        url = f"https://www.google.com/searchbyimage?hl=en-US&image_url={img_url}&start=0"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"}
        msg1 = await ctx.send(f"Searching {self.bot.get_custom_emoji('load.typing')}")
        async with self.bot.session.get(url, headers=headers, allow_redirects=True) as r:
            q = await r.read()
        await msg1.edit(content=f"Getting the result {self.bot.get_custom_emoji('load.typing')}")
        result = ""
        wrong = {
            "bonsai": "bonsly",
            "golet": "golette",
            "ポケモン ホルビー": "diggersby",
            "golett  go": " golett",
            "excalibur": "escavalier",
            "flower": "ralts",
            "tranquil": "tranquill",
            "shutterbug": "scatterbug",
            "fletching": "fletchling",
            "oricorio baile style": "oricorio",
            "sword and shield coal": "rolycoly",
            "psychic type cute physic pokemon": "skitty",
        }
        soup = BeautifulSoup(q.decode("utf-8"), "lxml")
        for best_guess in soup.findAll("a", class_="fKDtNb"):
            #  await ctx.send(best_guess)
            if not best_guess.get_text().replace("pokemon", "").strip().isdigit():
                raw_result = best_guess.get_text()
                result = (
                    best_guess.get_text()
                    .lower()
                    .replace("pokemon go", "")
                    .replace("pokemon", "")
                    .replace("png", "")
                    .replace("evolution", "")
                    .replace("shiny", "")
                    .replace("pokedex", "")
                    .replace("pokémon", "")
                    .strip()
                )
                if result in wrong:
                    result = wrong[result]
                break
            else:
                continue
        emby = discord.Embed(description=f"**p!catch {result}**", color=0x2F3136)
        emby.set_author(name=result)
        emby.set_image(url=img_url)
        emby.set_footer(
            text=f"Long press the p!catch {result} on mobile to copy quickly\n\nCommand Invoked by {ctx.author}\nRaw Result: {raw_result}",
            icon_url=ctx.author.avatar.url,
        )
        await ctx.send(embed=emby)
        await msg1.delete()
        #  kek = result.split(' ')
        #  await ctx.send(result[0])

    @commands.command(
        aliases=["sae", "getallemojis", "gae"],
    )
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.max_concurrency(1, BucketType.channel, wait=False)
    async def saveallemojis(self, ctx):
        """Saves all the emojis in the current server to a zip file and sends the zip file"""
        guild = ctx.guild
        guild_name = guild.name
        emojis = guild.emojis

        # If we already have a folder corresponding to the guild name, delete it
        # this can happen if the command was used previously and the bot stopped working
        if os.path.isdir(guild_name):
            shutil.rmtree(guild_name)
        os.makedirs(guild_name)

        # Lets estimate each emoji takes 0.25 seconds to download
        time_required = 0.25 * len(emojis)
        embed = discord.Embed(
            title=f"Saving {self.bot.get_custom_emoji('load.typing')}",
            description=f"This should take {round(time_required, 2)} seconds", # FIXME: use discord relative time
        )
        msg = await ctx.send(embed=embed)


        ###################
        # The saving part #
        ###################
        embed.add_field(
            name="Progress",
            value=f"0 {get_p(done / (len(emojis) / 100))} {len(emojis)}",
        )
        for done, item in enumerate(emojis,1):
            name = item.name
            ext = "." + str(item.url).rsplit(".")[-1]

            # We save the actual emoji to the folder
            await item.url.save(guild_name + "/" + name + ext)

            # We update the message each time pass 5 emojis (5,10,15,20,25,30,35,40,45,50...)
            if done // 5 == 0:
                time_required = 0.25 * (len(emojis) - done)
                embed = discord.Embed(
                    title=f"Saving {self.bot.get_custom_emoji('load.typing')}",
                    description=f"This should take {round(time_required, 2)} more seconds", # FIXME: use discord relative time
                )
                embed.add_field(
                    name="Progress",
                    value=f"{done} {get_p(done / (len(emojis) / 100))} {len(emojis)}",
                )
                await msg.edit(embed=embed)

        embed = discord.Embed(
            title=f"Zipping {self.bot.get_custom_emoji('load.typing')}",
            description="This should take a few more seconds",
        )
        await msg.edit(embed=embed)

        ####################
        # The zipping part #
        ####################
        directory = "./" + guild_name
        file_paths = get_all_file_paths(directory)
        filename = guild_name + "_emojis" + ".zip"

        with ZipFile(filename, "w") as zip:
            for file in file_paths:
                zip.write(file)

        size = humanize.naturalsize(os.path.getsize(filename), binary=True, format="%.3f")

        ############################
        # The message sending part #
        ############################
        await msg.delete()
        embed = discord.Embed(
            title="Completed",
            description=f"Task finished\n\nMade a zip file containing **{len(emojis)}** emojis in a **{size}** zip file",
            color=discord.Colour.green(),
        )
        embed.add_field(name="Original File size", value=size)
        embed.set_footer(
            text="Discord may show a different size since it stores some more metadata about the file in their database"
        )
        await ctx.send(embed=embed, file=discord.File(filename))
        # We remove the folder once we are done
        shutil.rmtree(guild_name)


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Utility(bot))

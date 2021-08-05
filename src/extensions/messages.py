import datetime
import json
import os
import re
import shutil
from io import StringIO
from typing import Optional, Union
from utils.functions import get_all_file_paths
from zipfile import ZipFile

import discord
import humanize
from discord.ext import commands
from discord.ext.commands import BucketType


class Messages(commands.Cog):
    """Message releated commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["fm"])
    async def firstmessage(self, ctx, channel: discord.TextChannel = None):
        """Sends the first message in a specified channel, defaults to the current channel"""
        channel = channel or ctx.channel
        first_message = None

        async for i in channel.history(oldest_first=True):
            first_message = i
        
        if not first_message:
            return await ctx.send("No first message found")
        
        embed = discord.Embed(title=f"First message in #{channel.name}", color=0x2F3136)
        embed.add_field(name="Message Author", value=first_message.author)
        
        if hasattr(first_message, "content") and first_message.content:
            embed.add_field(name="Message Content", value=first_message.content, inline=False)
        else:
            embed.add_field(name="Message Content", value="No message content", inline=False)
        
        if first_message.attachments:
            attachments = "\n".join(f"[{i.filename}]({i.url})" for i in first_message.attachments)
            embed.add_field(name="Attachments", value=attachments, inline=False)
        
        embed.add_field(
            name="Message sent at",
            value=f"{discord.utils.format_dt(first_message.created_at, 'R')} ({discord.utils.format_dt(first_message.created_at, 'R')})",
        )
        if first_message.edited_at:
            embed.add_field(
                name="Last edited at",
                value=f'{first_message.edited_at.strftime("%a, %d %B %Y, %H:%M:%S")}'
                      f'({humanize.precisedelta(datetime.datetime.utcnow() - first_message.edited_at)})',
            )
            
        embed.add_field(name="Jump to", value=first_message.jump_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["re"])
    @commands.cooldown(1, 5, BucketType.user)
    async def rawembed(self, ctx, message: discord.Message):
        """Shows raw embed json of a message gotten from the discord API"""
        res = await self.bot.http.get_message(message.channel.id, message.id)
        
        if not res["embeds"]:
            return await ctx.send("No embed found")
        
        data = json.dumps(res["embeds"][0], indent=4)
        
        if len(data) < 2000:
            await ctx.send(f"```json\n{data}```")
        else:
            await ctx.send(
                "Raw Content too large",
                file=discord.File(StringIO(data), filename="raw.json"),
            )

    @commands.command(aliases=["rj"])
    @commands.cooldown(1, 5, BucketType.user)
    async def rawjson(self, ctx, message: discord.Message):
        """Shows raw json of a message gotten from the discord API"""
        res = await self.bot.http.get_message(message.channel.id, message.id)
        data = json.dumps(res, indent=4)
        
        if len(data) < 2000:
            await ctx.send(f"{message.jump_url}\n```json\n{data}```")
        else:
            await ctx.send(
                "Raw Content too large",
                file=discord.File(StringIO(data), filename="raw.json"),
            )

    @commands.command(aliases=["rch"])
    @commands.cooldown(1, 5, BucketType.user)
    async def rawchannel(self, ctx, channel: discord.abc.GuildChannel):
        """Shows raw json of a channel gotten from the discord API"""
        res = await self.bot.http.get_channel(channel.id)
        data = json.dumps(res, indent=4)
        
        if len(data) < 4000:
            await ctx.send(f"```json\n{data}```")
        else:
            await ctx.send(
                "Raw Content too large",
                file=discord.File(StringIO(data), filename="rawchannel.json"),
            )

    @commands.command(aliases=["gm"])
    @commands.cooldown(1, 30, BucketType.user)
    @commands.max_concurrency(1, BucketType.channel, wait=False)
    async def getemojis(self, ctx, msg: discord.Message):
        """Gets all the emojis from a specified message and returns them in a zip file"""
        regex = r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>"
        path = "emojis"

        # If the folder exists we delete it
        if os.path.isdir(path):
            shutil.rmtree(path)
        # We create a new folder
        os.makedirs(path)

        # We get all the emojis and loop through them
        emos = re.finditer(regex, msg.content)
        
        for index, emo in enumerate(emos):
            ext, name, id = emo
            ext = "gif" if ext == "a" else "png"
            emo_url = f"https://cdn.discordapp.com/emojis/{id}.{ext}"
            async with self.bot.session.get(emo_url) as cs:
                byte = await cs.read()
                # We save them to a new file
                with open(f"{path}/{name}.{ext}", "wb") as f:
                    f.write(byte)

        # We get the file paths of all the emojis
        files = get_all_file_paths("./" + path)
        # We add the emojis to a zip file
        with ZipFile("emojis.zip", "w") as zip:
            for file in files:
                zip.write(file)
        # We send the zip file
        await ctx.send("Done", file=discord.File("emojis.zip"))
        # We remove the emojis folder
        shutil.rmtree("emojis")
        # We delete the zip file
        os.remove("emojis.zip")

    @commands.command(aliases=["rawuser", "rs"])
    @commands.cooldown(1, 5, BucketType.user)
    async def rawprofile(self, ctx, user: Union[discord.Member, discord.User, int]):
        """Shows raw json of a user's profile gotten from the discord API"""
        
        if isinstance(user, discord.Member):
            res = await self.bot.http.get_member(user.guild.id, user.id)
        else:
            user_id = user if isinstance(user, discord.User) else user.id
            res = await self.bot.http.get_user(user_id)
        
        data = json.dumps(res, indent=4)
        if len(data) < 4000:
            await ctx.send(f"```json\n{data}```")
        else:
            await ctx.send(
                "Raw Content too large",
                file=discord.File(StringIO(data), filename="rawprofile.json"),
            )

    @commands.command(aliases=["raw"])
    @commands.cooldown(1, 5, BucketType.user)
    async def rawmessage(self, ctx, message: discord.Message):
        """See a raw version of a message
        
        For example if someone sends a cool text formatted with bold/italics and stuff and you wanna copy it but keep the formatting"""
        res = discord.utils.escape_markdown(message.content)
        
        if len(res) > 4000:
            return await ctx.send(
                "Raw Content too large",
                file=discord.File(StringIO(res), filename="rawmessage.json"),
            )

        await ctx.send(res)

    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def messages(self, ctx, user: Optional[discord.Member] = None, channel: discord.TextChannel = None):
        """See someone's messages in a channel, defaults to the command invoker"""
        channel = channel or ctx.channel
        member = user or ctx.author
        
        msg = await ctx.send(f"Loading messages {self.bot.get_custom_emoji('load.typing')}")
        
        messages = await channel.history(limit=500).flatten()
        count = len([x for x in messages if x.author.id == member.id])
        perc = (100 * int(count)) / int(600)
        emb = discord.Embed(
            description=f"{'You' if member == ctx.author else member.name} sent **{count} ({perc}%)** messages in {channel.mention} in the last **500** messages."
        )
        
        await ctx.send(embed=emb)
        await msg.delete()

    @commands.command(description="See a list of top active users in a channel")
    @commands.max_concurrency(1, BucketType.channel, wait=True)
    async def top(self, ctx, limit=500, *, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        res = {}
        limit = min(limit, 1000)
        
        msg = await ctx.send(f"Loading messages {self.bot.get_custom_emoji('load.typing')}")
        # FIXME: use a better way to get the message count
        history = await channel.history(limit=limit).flatten()
        for i in history:
            res[i.author] = {"messages": len([j for j in history if j.author.id == i.author.id])}
        
        lb = sorted(res, key=lambda x: res[x].get("messages", 0), reverse=True)
        oof = ""
        counter = 0
        
        for i in lb:
            counter += 1
            if counter > 10:
                pass
            else:
                oof += f"{str(i):<20} :: {res[i]['messages']}\n"
        
        prolog = f"```prolog\n{'User':<20} :: Messages\n\n{oof}```"
        
        emb = discord.Embed(
            description=f"Top {channel.mention} users (last {limit} messages): {prolog}",
            colour=discord.Color.blurple(),
        )
        await ctx.send(embed=emb)
        await msg.delete()


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Messages(bot))

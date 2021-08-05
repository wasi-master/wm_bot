import datetime
import difflib
import inspect
import os
import pathlib
import time
from collections import Counter

import discord
import humanize
from discord.ext import commands
from discord.ext.commands import BucketType
from tabulate import tabulate

from utils.functions import get_random_color, make_permissions, split_by_slice
from utils.paginator import Paginator
from utils.classes import CodeStats


async def _basic_cleanup_strategy(self, ctx, search):
    count = 0
    async for msg in ctx.history(limit=search, before=ctx.message):
        if msg.author == ctx.me:
            await msg.delete()
            count += 1
    return {"Bot": count}


async def _complex_cleanup_strategy(self, ctx, search):
    prefix_for_this_guild = await self.bot.db.fetchrow(
        """
            SELECT prefix
            FROM guilds
            WHERE id=$1
            """,
        ctx.guild.id,
    )
    prefix = str(prefix_for_this_guild["prefix"])

    def check(m):
        return m.author == ctx.me or m.content.startswith(prefix)

    deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
    return Counter(m.author.display_name for m in deleted)


class MasterHelp(commands.HelpCommand):

    # !help
    async def send_bot_help(self, mapping):
        alteredmapping = dict()
        for cog, commands in list(mapping.items()):
            if cog is None:
                continue
            filtered = await self.filter_commands(commands, sort=True)
            if not filtered:
                continue
            alteredmapping[cog] = filtered
        items = []
        for page in split_by_slice(list(alteredmapping.items()), 6):
            emb = discord.Embed(
                title="Help",
                description=f"Total {len(self.context.bot.commands)} Commands",
                color=get_random_color(),
            )
            cogs = []
            for cog, commands in page:
                if cog is None:
                    continue
                filtered = await self.filter_commands(commands, sort=True)
                if not filtered:
                    continue
                commands_string = "".join(
                    f"`{command.qualified_name}`, " for command in filtered
                )
                cogs.append(cog.qualified_name)
                emb.add_field(
                    name=cog.qualified_name,
                    value=cog.description + "\n" + commands_string,
                    inline=True,
                )
            items.append(emb)
        menu = Paginator(embeds=items)
        await menu.start(self.context)
        if len(items) == 1:
            return await self.context.send(items[0])

    # !help <command>
    async def send_command_help(self, command):
        embed = discord.Embed()
        embed.title = command.qualified_name
        if command._buckets._cooldown:
            embed.add_field(
                name="Cooldown",
                value=f"{round(command._buckets._cooldown.per)} seconds per {command._buckets._cooldown.rate} command{'s' if command._buckets._cooldown.rate > 1 else ''} usage",
            )
        command_usage = await self.context.bot.db.fetchrow(
            """
                    SELECT *
                    FROM usages
                    WHERE name = $1;
                    """,
            command.name,
        )
        if not command_usage is None:
            embed.add_field(
                name="Popularity", value=f"Used {command_usage['usage']} times"
            )
        else:
            embed.add_field(name="Popularity", value="Command never used by anyone")
        if not command.help is None:
            embed.description = f"{command.description}\n\n{command.help}"
        else:
            embed.description = command.description or "No help found..."
        embed.add_field(
            name="Usage", value=self.get_command_signature(command), inline=False
        )
        if (image := command.extras.get("image")) is not None:
            embed.set_image(url=image)
        await self.context.send(embed=embed)

    # # !help <group>
    # async def send_group_help(self, group):
    #     await self.context.send("This is help group")

    # !help <cog>
    async def send_cog_help(self, cog):
        items = []
        commands = await self.filter_commands(cog.get_commands())
        for page in split_by_slice(commands, 6):
            embed = discord.Embed(
                title=f"{cog.qualified_name} Commands", color=get_random_color()
            )
            embed.set_footer(
                text="<x> means the argument x is required\n[x] means the argument x is optional\n[x=y] means the argument x is optional and has a default value of y"
            )
            for command in page:
                embed.add_field(
                    name=f"__{command.name}__ {command.signature}",
                    value=(command.help if command.help else command.description)
                    or "None",
                )
            items.append(embed)
        if len(items) == 1:
            return await self.context.send(embed=items[0])
        menu = Paginator(embeds=items)
        await menu.start(self.context)


class Meta(commands.Cog):
    """All the bot rleated commands"""

    def __init__(self, bot):
        self.bot = bot

        # Help command
        help_command = MasterHelp()
        help_command.cog = self
        help_command.command_attrs = dict(name="help", aliases=["h", "halp"])
        bot.help_command = help_command

    @commands.command(aliases=["cs"])
    async def commandsearch(self, ctx, cmd):
        """Search for a command in the bot"""
        if len(cmd) > 25:
            return await ctx.send("Name length too long")
        # Get all the commands and aliases and add them to a list
        all_commands_and_aliases = []
        for command in self.bot.commands:
            if command.aliases:
                for alias in command.aliases:
                    all_commands_and_aliases.append(alias)
            all_commands_and_aliases.append(command.name)
        # Get closest matching commands
        cmds = difflib.get_close_matches(cmd, all_commands_and_aliases, cutoff=0.3)
        # Send
        await ctx.send(
            embed=discord.Embed(
                title="Search results for " + cmd,
                description="\n".join(
                    [
                        f"**{index}.**  {command}"
                        for index, command in enumerate(cmds, start=1)
                    ]
                ),
            )
        )

    @commands.command()
    async def hello(self, ctx):
        """Use this to know if the bot is online or not"""
        await ctx.send("Hi im online :)")

    @commands.command(aliases=["linecount", "lc"])
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def lines(self, ctx):
        """Shows the amount of lines and some other information about the bot's code"""
        path = pathlib.Path("./")
        codestats = CodeStats()

        for file in path.rglob("*.py"):
            if str(file).startswith(("venv", ".")):
                continue

            codestats.filecount += 1

            with file.open(encoding="utf-8") as f:
                for line in f.readlines():
                    # This removes the tabs, spaces, and newline characters from the start and the end of the line
                    line = line.strip()

                    # Checks that check the start of the line
                    if line.startswith("class"):
                        codestats.classes += 1
                    elif line.startswith("def"):
                        codestats.functions += 1
                    elif line.startswith("async def"):
                        codestats.coroutines += 1
                    elif line.startswith("import"):
                        codestats.imports += 1
                    elif line.startswith("@commands.command"):
                        codestats.commands += 1
                    elif line.startswith('"""'):
                        codestats.docstrings += 1

                    # Checks that check for a specific word in the line
                    if "if" in line.split():
                        codestats.if_ += 1
                    if "else" in line.split():
                        codestats.else_ += 1
                    if "elif" in line.split():
                        codestats.elif_ += 1

                    # Checks that check for stuff anywhere in tbe line
                    if "#" in line:
                        codestats.comments += 1
                    if '"' in line or "'" in line:
                        codestats.strings += 1
                    if "discord.Embed" in line:
                        codestats.embeds += 1

                    codestats.lines += 1
                    codestats.characters += len(line)

        await ctx.send(
            content="**Code Satistics**\n"
            "```yaml\n"
            f"Files             :   {codestats.filecount:,}\n"
            f"Lines             :   {codestats.lines:,}\n"
            f"Characters        :   {codestats.characters:,}\n"
            f"Commands          :   {codestats.commands:,}\n"
            f"Imports           :   {codestats.imports:,}\n"
            f"Strings           :   {codestats.strings:,}\n"
            f"If Statements     :   {codestats.if_:,}\n"
            f"Else Statements   :   {codestats.else_:,}\n"
            f"Elif Statements   :   {codestats.elif_:,}\n"
            f"Classes           :   {codestats.classes:,}\n"
            f"Functions         :   {codestats.functions:,}\n"
            f"Docstrings        :   {codestats.docstrings:,}\n"
            f"Coroutines        :   {codestats.coroutines:,}\n"
            f"Embeds            :   {codestats.embeds:,}\n"
            f"Comments          :   {codestats.comments:,}"
            "```"
        )

    @commands.command(aliases=["p"], description="Shows the bot's speed")
    async def ping(self, ctx):
        start = time.time()
        embed = discord.Embed(
            description="**Websocket Latency** = Time it takes to receive data from the discord API\n**Response Time** = How long it took to send my message after recieving yours\n**Bot Latency** = Time needed to send/edit messages"
        )
        embed.set_author(name="Ping")
        embed.set_footer(text=f"Asked by {ctx.author}")
        embed.add_field(
            name="Websocket Latency", value=f"{round(self.bot.latency * 1000)}ms"
        )
        message = await ctx.send(embed=embed)
        end = time.time()
        message_ping = (end - start) * 1000
        embed.set_author(name="Ping")
        embed.set_footer(text=f"Asked by {ctx.author}")
        embed.add_field(
            name="Response Time",
            value=f"{round((message.created_at - ctx.message.created_at).total_seconds() * 1000)}ms",
        )
        embed.add_field(name="Bot Latency", value=f"{round(message_ping)}ms")
        await message.edit(embed=embed)

    @commands.command()
    async def support(self, ctx):
        """Get a invite link to the bot's support server"""
        await ctx.send(self.bot.config.support_server.invite)

    @commands.command(aliases=["info"])
    async def botinfo(self, ctx):
        """Lists some general stats about the bot."""
        await ctx.send(
            "Bot made by Wasi Master. Use these commands: `linecount`, `ping`, `help` for more info"
        )

    @commands.command(
        aliases=["sug", "suggestion", "rep", "report"],
    )
    @commands.cooldown(1, 3600, BucketType.user)
    async def suggest(self, ctx, *, suggestion: commands.clean_content):
        if self.bot.config.dm_suggestions:
            return await self.bot.owner.send(
                f"Suggestion by {ctx.author}: {suggestion}"
            )

        guild = self.bot.get_guild(576016234152198155)
        channel = guild.get_channel(740071107041689631)

        embed = discord.Embed(color=0x2F3136)
        embed.set_author(name="New Suggestion")
        embed.add_field(name="User", value=ctx.author)
        embed.add_field(name="Guild", value=ctx.guild.name)
        embed.add_field(name="Suggestion", value=f"```{str(suggestion)}```")

        message = await channel.send(embed=embed)
        await ctx.send("Suggestion sent")

        await message.add_reaction("\u2b06\ufe0f")  # upvote emoji
        await message.add_reaction("\u2b07\ufe0f")  # downvote emoji

    @commands.command(disabled=True)
    async def source(self, ctx, *, command: str = None):
        """Displays the bot's full source code or source code for a specific command.

        To display the source code of a subcommand you can separate it by
        periods, e.g. `tag.create` for the create subcommand of the tag command
        or by spaces e.g. `tag create`.
        """
        source_url = "https://github.com/wasi-master/wm_bot"
        branch = "master"

        if command is None:
            return await ctx.send(source_url)

        if command == "help":
            src = type(self.bot.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)
        else:
            obj = self.bot.get_command(command.replace(".", " "))
            if obj is None:
                return await ctx.send("Could not find command.")

            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith("discord"):
            # not a built-in command
            location = os.path.relpath(filename).replace("\\", "/")
        else:
            location = module.replace(".", "/") + ".py"
            source_url = "https://github.com/Rapptz/discord.py"
            branch = "master"

        final_url = f"<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>"
        await ctx.send(final_url)

    @commands.command(aliases=["usr", "user"])
    @commands.cooldown(1, 10, BucketType.user)
    async def users(self, ctx):
        """Shows the top 10 bot users"""
        command_usage = await self.bot.db.fetch(
            """
            SELECT *
            FROM users;
            """
            # TODO: make it sort by usage and return the top 10
        )
        dict_command_usage = {}
        for i in command_usage:
            user = self.bot.get_user(i["user_id"])
            dict_command_usage[str(user)] = i["usage"]
        dict_c_u = list(
            reversed(sorted(dict_command_usage.items(), key=lambda item: item[1]))
        )
        tabular = tabulate(
            dict_c_u[:10], headers=["User", "Commands Used"], tablefmt="fancy_grid"
        )
        await ctx.send(
            embed=discord.Embed(title="Top 10 Users", description=f"```{tabular}```")
        )

    @commands.command(
        aliases=["usg", "usages"], description="Shows usage statistics about commands"
    )
    @commands.cooldown(1, 10, BucketType.user)
    async def usage(self, ctx):
        command_usage = await self.bot.db.fetch(
            """
            SELECT *
            FROM usages;
            """
            # TODO: same as users
        )
        dict_command_usage = {}
        for i in command_usage:
            dict_command_usage[i["name"]] = i["usage"]
        dict_c_u = list(
            reversed(sorted(dict_command_usage.items(), key=lambda item: item[1]))
        )
        tabular = tabulate(
            dict_c_u[:15], headers=["Name", "Usage"], tablefmt="fancy_grid"
        )
        await ctx.send(
            embed=discord.Embed(title="Top 15 Commands", description=f"```{tabular}```")
        )

    @commands.command(aliases=["upt"])
    async def uptime(self, ctx):
        """Shows how long the bot is online for"""
        delta = datetime.datetime.utcnow() - ctx.bot.started_at
        precisedelta = humanize.precisedelta(delta, minimum_unit="seconds")
        naturalday = humanize.naturalday(ctx.bot.started_at)

        naturalday = (
            "" if naturalday == "today" else f"Bot is online since {naturalday}"
        )

        embed = discord.Embed(
            description=f"Bot is online for {precisedelta}\n{naturalday}"
        )
        embed.set_author(name="Bot Uptime")
        embed.set_footer(
            text=f"Note: This also means thr bot hasn't been updated for {precisedelta}"
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["clnup"])
    @commands.has_permissions(manage_messages=True)
    async def cleanup(self, ctx, search=100):
        """Cleans up the bot's messages from the channel.

        If a search number is specified, it searches that many messages to delete.
        If the bot has Manage Messages permissions then it will try to delete
        messages that look like they invoked the bot as well.
        After the cleanup is completed, the bot will send you a message with
        which people got their messages deleted and their count. This is useful
        to see which users are spammers.
        You must have Manage Messages permission to use this.
        """

        strategy = _basic_cleanup_strategy
        if ctx.me.permissions_in(ctx.channel).manage_messages:
            strategy = _complex_cleanup_strategy

        spammers = await strategy(self, ctx, search)
        deleted = sum(spammers.values())
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append("")
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f"- **{author}**: {count}" for author, count in spammers)

        await ctx.send("\n".join(messages), delete_after=10)

    @commands.command(
        aliases=["botinvite", "inv"]
    )
    async def invite(self, ctx, bot: discord.Member = None):
        """Send a invite link for the bot. if another bot is specified, sends the invite link for that bot instead"""
        bot = bot or ctx.me
        if not bot.bot:
            return await ctx.send("You must include a bot not a user")

        embed = discord.Embed(
            title=f"Invite for {bot.name}",
            description="**Here are the invites you can choose from:**\n\n",
            color=bot.color,
        )
        
        # These are either classmethods of discord.Permissions or the values of permissions
        perms = [8, "all", "none", 109640, "general", "voice", "text"]
        # We define all the variables
        admin, all_, none, suggested, default, voice, text = (make_permissions(i, oauth_url=bot.id) for i in perms)
        if ctx.guild:
            current = discord.utils.oauth_url(
                bot.id, permissions=bot.guild_permissions
            )
            
        # We make a description
        desc = (
            f'[Administrator]({admin} "Invite link with only the administrator permission")',
            f'[Current Permissions]({current} "Invite link with only the current server permissions")'
            if ctx.guild
            else "",
            f'[All Permissions]({all_} "Invite link with all permissions")',
            f'[No Permissions]({none} "Invite link with no permissions")',
            f'[Suggested Permissions]({suggested} "Invite link with suggested permissions")'
            if bot == ctx.me
            else "",
            f'[Default Permissions]({default} "Invite link with default permissions")',
            f'[Voice Permissions]({voice} "Invite link with all voice related permissions")',
            f'[Text Permissions]({text} "Invite link with text related permissions")',
        )
        # We set that as our description
        embed.description = embed.description + "\n".join(i for i in desc if i)
        await ctx.send(embed=embed)

    @commands.command(aliases=["statistics"])
    async def stats(self, ctx):
        """Sends some statistics about the bot"""
        embed = discord.Embed(color=0x2F3136)
        # Note: these are custom methods
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=False)
        embed.add_field(name="Members", value=len(self.bot.members), inline=False)
        embed.add_field(name="Unique Users", value=len(self.bot.users), inline=False)
        embed.add_field(name="Humans", value=len(self.bot.humans))
        embed.add_field(name="Bots", value=len(self.bot.members))

        await ctx.send(embed=embed)


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Meta(bot))

import datetime

import discord
import humanize
from discord.ext import commands
from utils.functions import format_name
import logging

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.logger.info("%s used by %s" % (ctx.command, ctx.author))

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.logger.info("%s finished by %s" % (ctx.command, ctx.author))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Sends a message to the owner when bot is added to a guild"""
        # We get the info
        guild_owner = self.bot.get_user(guild.owner_id)
        features = [format_name(i) for i in guild.features]
        # We make the embed
        embed = discord.Embed(
            title=f"Bot Added To {guild.name}",
            description=(
                f"Created At: {discord.utils.format_dt(guild.created_at, 'F')} "
                f"({discord.utils.format_dt(guild.created_at, 'R')})"
                f"ID: {guild.id}\n"
                f"Owner: {guild_owner}\n"
                f"Icon Url: [click here]({guild.icon.url})\n"
                f"Region: {str(guild.region)}\n"
                f"Members: {len(guild.members)}\n"
            ),
        )
        embed.set_thumbnail(url=guild.icon.url)
        # We send the message to the bot owner
        await self.bot.owner.send(embed=embed)
        # We add the prefix to our database
        await self.bot.db.execute(
            """
            INSERT INTO guilds (id, prefix)
            VALUES ($1, $2)
            """,
            guild.id,
            ",",
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Sends a message to the owner when bot is removed from a guild"""
        # We get the info
        guild_owner = self.bot.get_user(guild.owner_id)
        features = [format_name(i) for i in guild.features]
        # We make the embed
        embed = discord.Embed(
            title=f"Bot Removed From {guild.name}",
            description=(
                f"Created At: {discord.utils.format_dt(guild.created_at, 'F')} "
                f"({discord.utils.format_dt(guild.created_at, 'R')})"
                f"ID: {guild.id}\n"
                f"Owner: {guild_owner}\n"
                f"Icon Url: [click here]({guild.icon.url})\n"
                f"Region: {str(guild.region)}\n"
                f"Members: {len(guild.members)}\n"
            ),
        )
        embed.set_thumbnail(url=guild.icon.url)
        await self.bot.owner.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """We do some stuff, see the comments for more info"""

        # We remove this listener if there isn't a command_uses attribute to our bot,
        # This can happen when people copy paste the code here but do not make the attribute
        # We do not make the attribute ourselves because the person copying may not want this feature
        if not hasattr(self.bot, "command_uses"):
            return self.bot.remove_listener(self.on_message_delete)

        # If the message had invoked a command and was deleted, we delete the response to that message
        # If the response was not found or deleted then we just ignore it
        if message in self.bot.command_uses:
            self.logger.info("A message with a command %s was deleted by %s" % (message.content, message.author))
            try:
                await self.bot.command_uses[message].delete()
            except discord.NotFound:
                pass

        # We add the message to our snipes dictionary,
        self.bot.snipes[message.channel.id] = message

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """We do some stuff, see the comments for more info"""

        # We remove this listener if there isn't a command_uses attribute to our bot,
        # This can happen when people copy paste the code here but do not make the attribute
        # We do not make the attribute ourselves because the person copying may not want this feature
        if not hasattr(self.bot, "command_uses"):
            return self.bot.remove_listener(self.on_message_edit)

        if after.content and before.content != after.content:
            return

        # If the message had invoked a command and was edited, we delete the response
        # to that message and send a new response
        if before in self.bot.command_uses:
            self.logger.info("A message with a command %s was edited by %s" % (before.content, before.author))
            await self.bot.command_uses[before].delete()
            await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_message(self, message):
        """This is just for afk and mention detection"""

        # We remove this listener if there isn't a db attribute to our bot,
        # This can happen when people copy paste the code here but do not make the attribute
        # We do not make the attribute ourselves because the person copying should use their own db
        if not hasattr(self.bot, "db"):
            return self.bot.remove_listener(self.on_message)

        # We ignore, if the message author is a bot, if the message is in a dm
        if message.author.bot or message.guild is None:
            return

        # If the bot is mentioned then we send hi
        if message.guild.me.mention == message.content:
            prefix = "wm,"
            await message.reply(f"Hi, my prefix is {prefix}", mention_author=False)

        # OPTIMIZE: make it return if there isn't an afk person currently
        # We use an list just because a person can mention multiple afk people
        afk_people = []
        # We check if any person mentioned in the message is afk or not,
        # if they are we add them to the list
        for user in message.mentions:
            # TODO: use cache
            is_afk = await self.bot.db.fetchrow(
                """
                    SELECT *
                    FROM afk
                    WHERE user_id=$1;
                    """,
                user.id,
            )
            afk_people.append(is_afk)
        # If the list is empty then we don't do anything
        if not afk_people:
            return
        # If it is not empty then we notify the person
        for record in afk_people:
            if not record is None:
                await message.channel.send(
                    f"Hey {message.author.mention}, the person you mentioned: {self.bot.get_user(record['user_id'])} is currently afk for {humanize.naturaldelta(datetime.datetime.utcnow() - record['last_seen'])}\n\nreason: {record['reason']}"
                )

    @commands.Cog.listener()
    async def on_presence_update(self, old, new):
        """Logs the status change"""

        # There are some certain cases where we don't want to log the user
        if (
            new.status == old.status  # When the status stays the same
            or str(old.status) == "offline"  # When the user became online, we only log when the user becomesoffline
            or len(new.guild.members) < 500  # The server is a big server
        ):
            return
        time = datetime.datetime.utcnow()
        # OPTIMIZE: Make it use cache or one db call
        status = await self.bot.db.fetchrow(
            """
                SELECT *
                FROM status
                WHERE user_id=$1
                """,
            new.id,
        )

        if status is None:
            await self.bot.db.execute(
                """
                        INSERT INTO status (last_seen, user_id)
                        VALUES ($1, $2)
                        """,
                time,
                new.id,
            )
        else:
            await self.bot.db.execute(
                """
                    UPDATE status
                    SET last_seen = $2
                    WHERE user_id = $1;
                    """,
                new.id,
                time,
            )


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Events(bot))

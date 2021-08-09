"""File for things releated to the bot."""
import asyncio
import os
from operator import attrgetter
from typing import Generator, List, Union

import aiogoogletrans
import aiohttp
import async_cleverbot
import async_cse
import asyncdagpi
import asyncpg
import discord
from akinator.async_aki import Akinator
from discord.ext import commands
from dotenv import load_dotenv
from playsound import PlaysoundException, playsound

from utils.classes import BlackListed, Config, CustomEmojis
from utils.functions import load_json, read_file

__all__ = ("WMBot", "WMBotContext")

async def get_prefix(_bot, message):
    """Use this to fetch the current servers prefix from the db.

    Parameters
    ----------
        _bot (commands.Bot): The bot to get the prefix of
        message (discord.Message): the message to get some metadata

    Returns
    -------
        typing.Union[str, List[str]]: prefix


    """
    if isinstance(message.channel, discord.DMChannel):
        return _bot.config.dm_prefix

    if message.author == _bot.owner:
        return _bot.config.owner_prefix

    prefix_for_this_guild = await _bot.db.fetchrow(
        """
            SELECT prefix
            FROM guilds
            WHERE id=$1
            """,
        message.guild.id,
    )

    if prefix_for_this_guild is None:
        await _bot.db.execute(
            """
                INSERT INTO guilds (id, prefix)
                VALUES ($1, $2)
                """,
            message.guild.id,
            ",",
        )
        prefix_for_this_guild = {"prefix": _bot.config.default_prefix}

    prefix_return = str(prefix_for_this_guild["prefix"])
    return commands.when_mentioned_or(prefix_return)(_bot, message)


class WMBot(commands.Bot):
    """A subclass of commands.Bot."""

    def __init__(self, *, specified_loop=None):
        """Makes a instance of WMBot."""
        intents = discord.Intents(
            members=True,
            presences=True,
            guilds=True,
            emojis=True,
            invites=True,
            messages=True,
            reactions=True,
            voice_states=True,
        )
        loop = asyncio.get_event_loop()
        session = aiohttp.ClientSession(loop=loop)

        # Load all the environment variables
        load_dotenv("config/Bot/token.env")
        load_dotenv("config/Apis/tokens.env")
        load_dotenv("config/Database/db.env")

        # Read the emoji file
        self.emoji_config = CustomEmojis.from_json(read_file("config/General/emojis.json"))
        # Read the config file
        self.config = Config.from_json(read_file("config/General/config.json"))

        # Set the HTTPException error codes dict to a custom property for easy access
        self.httpexception_codes = load_json("assets/data/httpexception_codes.json", make_keys_int=True)

        # APIs
        self.cleverbot = async_cleverbot.Cleverbot(
            os.environ["cleverbot"],
            session=session,
            context=async_cleverbot.DictContext(),
        )
        self.dagpi = asyncdagpi.Client(os.environ["dagpi"])
        self.google_api = async_cse.Search(os.environ["google_search"], session=session)
        self.translate_api = aiogoogletrans.Translator()
        self.aki = Akinator()
        self.apis = ["OMDB", "tenor", "owlbot", "gender_api"]
        self.api_keys = {api: os.environ[api.lower()] for api in self.apis}

        # For the snipe command
        self.snipes = {}

        # For tracking commands
        self.command_uses = {}

        # For api requests
        self.session = session

        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True,
            intents=intents,
            session=session,
            loop=specified_loop or loop,
            strip_after_prefix=True,
            owner_ids=self.config.owner_ids,
        )

        # For before_invoke
        self._before_invoke = self.before_invoke
        # For blacklisted check
        self._checks.append(self.bot_check)

    async def get_context(self, message: discord.Message, *, cls: commands.Context = None) -> commands.Context:
        """Return the custom context."""
        return await super().get_context(message, cls=cls or WMBotContext)

    async def close(self):
        await self.session.close()
        await super().close()

    async def fetch_banner(self, user: discord.User) -> str:
        # TODO: Cache
        tempuser = await self.fetch_user(user.id)
        return tempuser.banner.url if tempuser.banner else None


    @property
    def owner(self) -> discord.User:
        """Call to get the owner of the bot."""
        if self.config.owner_id:
            return self.get_user(self.config.owner_id)
        if self.owner_ids:
            return self.get_user(self.config.owner_ids[0])
        return None

    @property
    def members(self) -> Generator[discord.Member, None, None]:
        """Use this to get all the members of the bot"""
        for guild in self.guilds:
            for member in guild.members:
                yield member

    @property
    def member_count(self) -> List[discord.Member]:
        """Use this to get all the members of the bot"""
        return sum([g.member_count for g in self.guilds])

    @property
    def humans(self) -> Generator[discord.User, None, None]:
        """Use this to get all the members of the bot"""
        for user in self.users:
            if not user.bot:
                yield user
    
    @property
    def bots(self) -> Generator[discord.User, None, None]:
        """Use this to get all the members of the bot"""
        for user in self.users:
            if user.bot:
                yield user

    def get_config_emoji(self, emoji_name: str) -> str:
        """Gets a emoji from the bot config.

        Parameters
        ----------
        emoji_name : str
            the emoji that it needs to get

        Returns
        -------
        str
            the emoji that it got, can be empty if it was not found
        """
        return attrgetter(emoji_name)(self.emoji_config)

    def get_user_named(self, name: str) -> Union[discord.User, None]:
        """Gets a user with the given name from the bot

        Parameters
        ----------
        name : str
            The name of the user, can have the discriminator

        Returns
        -------
        Union[discord.User, None]
            The user if it was found, otherwise None
        """
        result = None
        users = self.users

        if len(name) > 5 and name[-5] == "#":
            # The 5 length is checking to see if #0000 is in the string,
            # as a#0000 has a length of 6, the minimum for a potential
            # discriminator lookup.
            potential_discriminator = name[-4:]

            # do the actual lookup and return if found
            # if it isn't found then we'll do a full name lookup below.
            result = discord.utils.get(users, name=name[:-5], discriminator=potential_discriminator)
            if result is not None:
                return result

        def pred(user):
            return user.nick == name or user.name == name

        return discord.utils.find(pred, users)

    async def before_invoke(self, ctx):
        """
        Starts typing in the channel to let the user know that the bot received the command and is working on it.

        Parameters
        ----------
        ctx : commands.Context
            Represents the context in which a command is being invoked under.
        """
        await ctx.channel.trigger_typing()

    async def on_command_completion(self, ctx):
        """Saves the command usage to database"""
        command_name = ctx.command.qualified_name
        usage = await self.db.fetchrow(
            """
                SELECT usage
                FROM usages
                WHERE name=$1
                """,
            command_name,
        )
        if usage is None:
            await self.db.execute(
                """
                    INSERT INTO usages (usage, name)
                    VALUES ($1, $2)
                    """,
                1,
                command_name,
            )
        else:
            usage = usage["usage"]
            usage += 1
            await self.db.execute(
                """
                    UPDATE usages
                    SET usage = $2
                    WHERE name = $1;
                    """,
                command_name,
                usage,
            )

    async def on_command(self, ctx):
        """Saves the details about the user of the command

        Parameters
        ----------
            ctx (commands.Context): Represents the context in which
            a command is being invoked under.
        """
        user_id = ctx.author.id
        usage = await self.db.fetchrow(
            """
                SELECT usage
                FROM users
                WHERE user_id=$1
                """,
            user_id,
        )
        if usage is None:
            await self.db.execute(
                """
                    INSERT INTO users (usage, user_id)
                    VALUES ($1, $2)
                    """,
                1,
                user_id,
            )
        else:
            usage = usage["usage"]
            usage += 1
            await self.db.execute(
                """
                    UPDATE users
                    SET usage = $2
                    WHERE user_id = $1;
                    """,
                user_id,
                usage,
            )

    async def bot_check(self, ctx):
        """Checks if the user is blocked

        Parameters
        ----------
            ctx (commands.Context): the context in which the command was executed in

        Raises
        -------
            BlackListed: error to be catched in the error handler

        Returns
        -------
            bool: if the user can use the command
        """
        blocked = await self.db.fetchrow(
            """
            SELECT *
            FROM blocks
            WHERE user_id=$1
            """,
            ctx.author.id,
        )
        if blocked is None:
            return True
        raise BlackListed


class WMBotContext(commands.Context):
    """A subclass of commands.Context."""

    @property
    def owner(self) -> None:
        """Call to get the owner of the bot."""
        return self.bot.get_user(self.bot.config.owner_ids[0])

    async def send(self, *args, **kwargs) -> discord.Message:
        """Use this to send a message."""
        if kwargs.get("no_reply") is True:
            return await self.send(*args, **kwargs)
        # Wrapping this in a try/except block because the original message can be deleted.
        # and if it is deleted then we won't be able to reply and it will raise an error
        try:
            # First we try to reply
            message = await self.reply(*args, **kwargs)
        except discord.NotFound:
            # If the original message was deleted, we just send it normally
            message = await self.send(*args, **kwargs, no_reply=True)
        if not hasattr(self.bot, "command_uses"):
            # If for some reason the command_uses is not there, we just add it
            self.bot.command_uses = {}
        # We add the current message to the command_uses dictionary for tracking
        self.bot.command_uses[self.message] = message
        # We return the message because this is the intended behaviour of commands.Context.send
        return message


async def create_db_pool(bot):
    """Connects to the db and sets it as a variable"""
    bot.db = await asyncpg.create_pool(
        host=os.environ["host"],
        database=os.environ["database"],
        user=os.environ["user"],
        password=os.environ["password"],
        ssl=os.environ["ssl"],
    )
    # We try to play a sound to let the user know that the bot is online
    # If the sound playing fails we just ignore it
    try:
        playsound("assets/sounds/connected_to_database.mp3", block=False)
    except PlaysoundException:
        pass

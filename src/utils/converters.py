"""A file to keep all the converters."""
import collections
import inspect
import re
from typing import Deque, Optional

from discord.ext import commands

__all__ = (
    "Codeblock",
    "CodeblockConverter",
    "LanguageConverter",
    "TagName",
    "TimeConverter",
)

time_regex = re.compile(r"(\d{1,5}(?:[.,]?\d{1,5})?)([smhd])")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400, "mo": 2592000}


class WMBotConverter(commands.Converter):
    """A subclass of commands.Converter to handle parameters."""

    def get_param_name(self, ctx: commands.Context) -> Optional[str]:
        """Returns the name of the parameter where the converter was used

        Parameters
        ----------
        ctx : commands.Context
            The context, used to get the command signature.

        Returns
        -------
        Optional[str]
            the parameter name, or None if not found.
        """
        typehint_regex = rf"(?P<param_name>[A-Za-z_]+)\s*:\s*(?P<module>[A-Za-z_]+\.)?(?P<typehint_class>{self.__class__.__name__})"
        sig = str(inspect.signature(ctx.command.callback))
        param_name = re.search(typehint_regex, sig)
        return param_name.group("param_name") if param_name else "None"


class TimeConverter(WMBotConverter):
    """Converts time from a string to a number.

    Examples
    --------
    15m = 15 minutes
    120s = 120 seconds
    6h = 6 hours
    7d = 7 days
    1mo = 1 month
    You can also use multiple time strings combined into one string
    1h15m = 1 hour 15 minutes
    1d6h30m = 1 day 6 hours 30 minutes
    1mo15d = 1 month 15 days
    You can also use time strings with decimal places
    1.5m = 1 minute 30 seconds
    1.255d = 1 day 6 hours 30 minutes
    """

    async def convert(self, ctx: commands.Context, argument: str) -> int:
        """Do the actual conversion."""
        matches = time_regex.findall(argument.lower())
        if not matches:
            raise commands.BadArgument(
                f'Converting to "Time" failed for parameter "{self.get_param_name(ctx)}":'
                f"The time is empty or invalid"
            )
        time = 0.0
        for value, key in matches:
            try:
                time += time_dict[key] * float(value)
            except KeyError:
                raise commands.BadArgument(
                    f'Converting to "Time" failed for parameter "{self.get_param_name(ctx)}":'
                    f"{key} is an invalid time-key! h/m/s/d are valid!"
                )
            except ValueError:
                raise commands.BadArgument(
                    f'Converting to "Time" failed for parameter "{self.get_param_name(ctx)}":'
                    f"{value} is not a number!"
                )
        # We convert it to int because we don't want it to be milisecond precise
        return int(time)


class LanguageConverter(WMBotConverter):
    """Converts a language"""

    async def convert(self, ctx: commands.Context, lang: str) -> str:
        """Converts a language and returns it's full name

        Parameters
        ----------
        ctx : commands.Context
            The context of the commands
        lang : str
            The language to convert

        Returns
        -------
        str
            The language's full name

        Raises
        ------
        commands.BadArgument
            If the language is invalid
        """
        if lang in ctx.bot.language_codes:
            lang = ctx.bot.language_codes[lang]
        elif lang in ctx.bot.language_codes.values():
            lang = lang
        else:
            raise commands.BadArgument(
                f'Converting to "Language" failed for parameter "{self.get_param_name(ctx)}"'
                f":Unknown language"
            )
        if lang == "zh":
            lang = "zh-CN"
        return lang


Codeblock = collections.namedtuple("Codeblock", "language content")


class CodeblockConverter(WMBotConverter):
    """
    A converter that strips codeblock markdown if it exists.

    Returns a namedtuple of (language, content).
    :attr:`Codeblock.language` is an empty string if no language was given with this codeblock.
    It is ``None`` if the input was not a complete codeblock.
    """

    async def convert(self, ctx: commands.Context, argument: str) -> Codeblock:
        """Do the actual conversion."""
        if not argument.startswith("`"):
            return Codeblock(None, argument)

        # keep a small buffer of the last chars we've seen
        last: Deque[str] = collections.deque(maxlen=3)
        backticks = 0
        in_language = False
        in_code = False
        language = []
        code = []

        for char in argument:
            if char == "`" and not in_code and not in_language:
                backticks += 1  # to help keep track of closing backticks
            if (
                last
                and last[-1] == "`"
                and char != "`"
                or in_code
                and "".join(last) != "`" * backticks
            ):
                in_code = True
                code.append(char)
            if char == "\n":  # \n delimits language and code
                in_language = False
                in_code = True
            # we're not seeing a newline yet but we also passed the opening ```
            elif "".join(last) == "`" * 3 and char != "`":
                in_language = True
                language.append(char)
            # we're in the language after the first non-backtick character:
            elif in_language:
                if char != "\n":
                    language.append(char)

            last.append(char)

        if not code and not language:
            code[:] = last

        return Codeblock("".join(language), "".join(code[len(language) : -backticks]))


class TagName(WMBotConverter):
    """Checks if the tag exists."""

    async def convert(self, ctx: commands.Context, argument: str) -> str:
        """Do the actual conversion."""
        tag = await ctx.bot.db.fetch(
            """
            SELECT * FROM tags WHERE NAME = $1
            """,
            argument,
        )
        if not tag:
            raise commands.BadArgument(
                f'Converting to "Tag" failed for parameter "{self.get_param_name(ctx)}":'
                f"Tag {argument} doesn't exist"
            )
        return tag

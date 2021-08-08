"""Has some usefull functions for the bot"""
import asyncio
import datetime
import functools
import inspect
import json
import os
import random
import re
from operator import attrgetter
import pprint
from typing import Any, AnyStr, Callable, Coroutine, Dict, Iterable, List, Union

import discord
import numpy as np
import rich
from discord.ext import commands
from rich.console import Console
from rich.syntax import Syntax

from utils.classes import CustomEmojis

VALID_JSON_TYPES = Union[str, int, bool, list, dict, None]

__all__ = (
    "button_from_json",
    "closest_smaller",
    "compare_date",
    "convert_sec_to_min",
    "executor_function",
    "find_user_named",
    "format_name",
    "get_agreement",
    "get_all_customs",
    "get_all_file_paths",
    "get_bool",
    "get_country_emoji",
    "get_custom_emoji",
    "get_flag",
    "get_image",
    "get_p",
    "get_random_color",
    "get_status",
    "is_image",
    "levenshtein_match_calc",
    "load_json",
    "make_permissions",
    "print_error",
    "read_file",
    "split_by_slice",
    "write_file",
)

def button_from_json(json_obj: dict, *, cls: Any = discord.ui.Button) -> discord.Button:
    """A function that returns a button from a JSON dictionary

    Parameters
    ----------
    json_obj : dict
        the json dictionary representing the button
    cls: Object
        The class to use for the button

    Returns
    -------
    discord.Button
        The button that was converted from the JSON
    """
    button = cls(
        label=json_obj.get("label", ""),
        style=json_obj.get("style", ""),
        disabled=json_obj.get("disabled", False),
        row=json_obj.get("row", 0),
    )
    if json_obj.get("emoji"):
        button.emoji = json_obj["emoji"]
    return button


def closest_smaller(list_of_numbers: Iterable[int], number: int) -> int:
    """Returns the closest number that is smaller that the given number.

    Examples
    --------
    >>> l = [1, 4, 9, 16, 25]
    >>> n = 19
    >>> closest_smaller(l, n)
    16

    Parameters
    ----------
    list_of_numbers: Iterable[int]
        The numbers to get the closest from
    number: int
        The number to get the closest of

    Returns
    -------
    int
        The closest smaller number
    """
    return min(list_of_numbers, key=lambda x: abs(x - number))


def compare_date(a: datetime.date, b: datetime.date) -> bool:
    """Compares two dates and returns True if they have the same month and day, does not take year into count

    Examples
    --------
    >>> compare_date(datetime.date(2016, 1, 1), datetime.date(2019, 1, 1))
    True
    >>> compare_date(datetime.date(2016, 7, 5), datetime.date(2019, 1, 1))
    False

    Parameters
    ----------
    a : datetime.date
        the first time
    b : datetime.date
        the second time

    Returns
    -------
    bool
        True if the dates are the same excluding year else False
    """
    return a.day == b.day and a.month == b.month


def convert_sec_to_min(seconds) -> str:
    """Converts a second to a minute:second format

    Examples
    --------
    >>> convert_sec_to_min(0)
    '0:00'
    >>> convert_sec_to_min(60)
    '1:00'
    >>> convert_sec_to_min(90)
    '1:30'
    >>> convert_sec_to_min(912):
    '15:12'

    Parameters
    ----------
    seconds: int
        the seconds to convert the data from

    Returns
    -------
        str: the formatted output
    """
    minutes, sec = divmod(seconds, 60)
    return "%02d:%02d" % (minutes, sec)


def executor_function(sync_function: Callable) -> Coroutine:
    """Converts a function to a async function that runs in an executor

    Parameters
    ----------
    sync_function: Callable
        The function to convert

    Returns
    -------
    Coroutine
        The converted function
    """

    @functools.wraps(sync_function)
    async def sync_wrapper(*args, **kwargs):
        """
        Asynchronous function that wraps a sync function with an executor.
        """

        loop = asyncio.get_event_loop()
        internal_function = functools.partial(sync_function, *args, **kwargs)
        return await loop.run_in_executor(None, internal_function)

    return sync_wrapper


def find_user_named(users: Iterable[discord.User], name: str) -> discord.User:
    result = None

    if len(name) > 5 and name[-5] == "#":
        # The 5 length is checking to see if #0000 is in the string,
        # as a#0000 has a length of 6, the minimum for a potential
        # discriminator lookup.
        potential_discriminator = name[-4:]

        # do the actual lookup and return if found
        # if it isn't found then we'll do a full name lookup below.
        result = discord.utils.get(
            users, name=name[:-5], discriminator=potential_discriminator
        )
        if result is not None:
            return result

    def pred(user):
        return user.nick == name or user.name == name

    return discord.utils.find(pred, users)


def format_name(name: str) -> str:
    """Formats a string for displaying to the user

    Examples
    --------
    >>> format_name("manage_messages")
    'Manage Messages'
    >>> format_name("some_name")
    'Some Name'

    Parameters
    ----------
    name : str
        the raw name

    Returns
    -------
    str
        the formatted name
    """
    return name.replace("_", " ").title().strip()


async def get_agreement(
    ctx: commands.Context,
    text: str,
    destination: discord.abc.Messageable = None,
    target: discord.User = None,
    timeout: int = 20,
) -> Union[bool, None]:
    """Return if the user agreed or not

    Parameters
    ----------
    ctx : commands.Context
        The context of the command
    text : str
        The message to send to ask the user for their confirmation
    destination : discord.abc.Messageable, optional
        Where to send the message to, this kwarg exists to dm the user, by default ctx.channel
    target : discord.User, optional
        The person that should respond to the message, by default ctx.author
    timeout : int, optional
        How long to wait for the user to respond, by default 20

    Returns
    -------
    Union[bool, None]
        If the user agreed or not, can be None if user gives invalid response
    """

    destination = destination or ctx.channel
    target = target or ctx.author

    def check(msg):
        return msg.author.id == target.id and msg.channel.id == destination.id

    await destination.send(text + " type `yes` or `no`")
    try:
        response = await ctx.bot.wait_for("message", check=check, timeout=timeout)
    except asyncio.TimeoutError:

        if isinstance(destination, commands.Context):
            await ctx.reply("You didn't respond in 30 seconds :(")
        else:
            await destination.send("You didn't respond in 30 seconds :(")

        return False
    else:
        return get_bool(response.content)


def get_all_customs(
    obj: Any, syntax_highlighting: bool = False, print_to_console: bool = False
) -> str:
    """Gets all the custom attributes of the object

    Parameters
    ----------
    obj : Any
        The object to get the attributes from
    syntax_highlighting : bool, optional
        Whether to use syntax highlighting for the output, by default False
    print_to_console : bool, optional
        Whether to print the output to the console, by default False

    Returns
    -------
    str
        All The attributes of the object
    """
    dicted = {}
    for i in dir(obj):
        if not str(i).startswith("__") and not str(getattr(obj, i)).startswith("<"):
            attr = getattr(obj, i)
            if isinstance(attr, int):
                dicted[i] = int(attr)
            elif attr is None:
                dicted[i] = None
            elif isinstance(attr, bool):
                dicted[i] = attr
            else:
                dicted[i] = str(attr)
    dicted = pprint.pformat(dicted, indent=4, width=50)
    if print_to_console:
        syntax = Syntax(dicted, "python", theme="monokai", line_numbers=True)
        console = Console()
        console.print(syntax)
    return (
        ("```python\n" if syntax_highlighting else "")
        + dicted
        + ("```" if syntax_highlighting else "")
    )


def get_all_file_paths(directory: str) -> List[str]:
    """Returns the file paths of all the files in the specified directory

    Parameters
    ----------
    directory : str
        The directory to search for files

    Returns
    -------
    List[str]
        The list of file paths
    """
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths


def get_bool(value: str) -> Union[bool, None]:
    """When given a string, returns a boolean value based on the string

    Parameters
    ----------
    value : str
        A string representing a user response

    Returns
    -------
    Union[bool, None]
        whether the string is truethy or falsey
    """
    lowered = str(value).lower()

    if lowered in ("yes", "y", "true", "t", "1", "enable", "on"):
        val = True
    elif lowered in ("no", "n", "false", "f", "0", "disable", "off"):
        val = False
    else:
        val = None

    return val


def get_country_emoji(countrycode: str) -> str:
    """Returns the emoji of the given country

    Parameters
    ----------
    countrycode : str
        The country code of the country, eg. US

    Returns
    -------
        str: the emoji of the country
    """
    offset = 127397  # gotten from `ord("🇦") - ord("A")``

    return "".join([chr(ord(c.upper()) + offset) for c in countrycode])


def get_custom_emoji(emoji: str) -> str:
    """Returns the custom emoji from the config if it exists

    Parameters
    ----------
    emoji : str
        the emoji to get

    Returns
    -------
    str
        The emoji that it got
    """
    emoji_config = CustomEmojis.from_json(read_file("config/General/emojis.json"))
    return attrgetter(emoji)(emoji_config)


def get_flag(flag: str) -> str:
    """Gets a flag emoji from the flag name

    Parameters
    ----------
    flag : str
        The flag name, discord.User.public_flags is a good way to get all the flags

    Returns
    -------
    str
        The emoji the flag corresponds to
    """
    flag = flag.name
    if flag == "hypesquad_brilliance":
        return " \
        | HypeSquad Brilliance"

    elif flag == "hypesquad_bravery":
        return f"{get_custom_emoji('badges.hypesquad.bravery')} | HypeSquad Bravery"
    elif flag == "hypesquad_balance":
        return f"{get_custom_emoji('badges.hypesquad.balance')} | HypeSquad Balance"
    elif flag == "hypesquad":
        return f"{get_custom_emoji('badges.hypesquad_events')} | HypeSquad Events"
    elif flag == "early_supporter":
        return f"{get_custom_emoji('badges.early_supporter')} | Early Supporter"
    elif flag == "bug_hunter":
        return f"{get_custom_emoji('badges.bug_hunter_1')} | Bug Hunter"
    elif flag == "bug_hunter_level_2":
        return f"{get_custom_emoji('badges.bug_hunter_2')} | Bug Hunter Level 2"
    elif flag == "verified_bot_developer":
        return (
            f"{get_custom_emoji('badges.verified_bot_dev')} |"
            "Early Verified Bot Developer"
        )
    elif flag == "verified_bot":
        return f"{get_custom_emoji('badges.verified_bot')} | Verified Bot"
    elif flag == "partner":
        return f"{get_custom_emoji('badges.discord_partner')} | Discord Partner"
    elif flag == "staff":
        return "Discord Staff"
    else:
        return flag.title().replace("_", "")


async def get_image(
    ctx: commands.Context,
    item: Union[discord.Member, discord.Emoji, discord.PartialEmoji, None, str] = None,
):
    """Returns a image url from the data given

    Parameters
    ----------
    ctx : commands.Context
        the context in which the command was called
    url : typing.Union[ discord.Member, discord.Emoji, discord.PartialEmoji, None, str ], optional
        [description], by default None

    Returns
    -------
    str
        the url of the image
    """

    # Check if it's a emoji
    if isinstance(item, str) and not is_image(item):
        item = f"https://twemoji.maxcdn.com/v/latest/72x72/{ord(item):x}.png"
        # We return the item if it is valid
        if (await ctx.bot.session.get(item)).status == 200:
            return item
    # If the message is replying to another message
    if ctx.message.reference:
        ref = ctx.message.reference.resolved
        # If the reference message has a embed we return
        # the image url if it is not empty and if it is empty
        # then we return the thumbnail url
        if ref.embeds:
            if ref.embeds[0].image.url != discord.Embed.Empty:
                if is_image(ref.embeds[0].image.url):
                    return ref.embeds[0].image.url

            if ref.embeds[0].thumbnail.url != discord.Embed.Empty:
                if is_image(ref.embeds[0].thumbnail.url):
                    return ref.embeds[0].thumbnail.url
        # If the referenced message has attachments we return the url of the first one
        elif ref.attachments:
            item = ref.attachments[0].url or ref.attachments[0].proxy_url
            if is_image(item):
                return item
    # If the user mentioned a member then we use their avatar
    if isinstance(item, discord.Member):
        return str(item.avatar.with_format("png"))
    # If the text is a string but not a emoji
    elif isinstance(item, str):
        if is_image(item):
            return item
    # If it is something with a url attribute, most probably a asset or a emoji, then we return that
    if hasattr(item, "url"):
        return item.url
    # If the user's message has a attachment, we return the url of the attachment
    if ctx.message.attachments:

        item = ctx.message.attachments[0].url or ctx.message.attachments[0].proxy_url

        if is_image(item):
            return (
                ctx.message.attachments[0].proxy_url or ctx.message.attachments[0].url
            )

    if item is None:
        return str(ctx.author.avatar.with_format("png"))


def get_p(
    progress: int,
    *,
    total=100,
    prefix="",
    suffix="",
    decimals=0,
    length=100,
    fill="█",
):
    """Use this to make a progress bar for

    Parameters
    ----------
    progress : int
        the current progress
    total : int, optional
        the total progress, by default 100
    prefix : str, optional
        the prefix to add in front of the progressbar, by default ""
    suffix : str, optional
        the suffix to add in front of the progressbar, by default ""
    decimals : int, optional
        the number of decimal places to display in the progressbar, by default 0
    length : int, optional
        the length of the progressbar, by default 100
    fill : str, optional
        the fill to add use the progressbar, by default "█"

    Returns
    -------
    str
        the progressbar
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (progress / total))
    filled_length = int(length * progress // total)
    bar = fill * filled_length + "-" * (length - filled_length)
    return f"{prefix} |{bar}| {percent}% {suffix}"


def get_random_color() -> discord.Color:
    """Returns a random color from discord.Color

    Returns
    -------
    discord.Color
        The random color that was picked
    """
    # We randomly pick a color
    return discord.Color(random.randint(0, 0xFFFFFF))


def get_status(status: str) -> str:
    """Returns the status emoji

    Parameters
    ----------
    status : str
        the status to convert one of online / idle / dnd / offline

    Returns
    -------
    str
        The emoji for the status, can be the raw status if the status does not have any emoji
    """
    valid_statuses = ["online", "idle", "dnd", "offline"]
    # We check if the status is valid
    if str(status) in valid_statuses:
        # We return the custom emoji for the status
        return get_custom_emoji(f"status.{status}")
    else:
        # We just return the raw status
        return status


def is_image(url: str) -> bool:
    """If a image is a valid image or not.

    Examples
    ________
    >>> url = "https://i.imgur.com/a/MzgxNjI.jpg"
    >>> is_image(url)
    True
    >>> url = "https://www.google.com"
    >>> is_image(url)
    False

    Parameters
    ----------
    url : str
        The url to validate

    Returns
    -------
    bool
        The image is a valid image or not
    """
    # We cast it to bool just to make sure that it is True/False
    return bool(re.match(r"(https?:\/\/.*\.(?:png|jpg))", url))


def levenshtein_match_calc(s: Iterable, t: Iterable) -> float:
    """Matches 2 items and returns the percentage of the match

    Parameters
    ----------
    s : Iterable
        The first item to match
    t : Iterable
        The second item to match

    Returns
    -------
    int
        The percentage of the match
    """
    rows = len(s) + 1
    cols = len(t) + 1
    distance = np.zeros((rows, cols), dtype=int)

    for i in range(1, rows):
        for k in range(1, cols):
            distance[i][0] = i
            distance[0][k] = k

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row - 1] == t[col - 1]:
                cost = 0
            else:
                cost = 2
            distance[row][col] = min(
                distance[row - 1][col] + 1,  # Cost of deletions
                distance[row][col - 1] + 1,  # Cost of insertions
                distance[row - 1][col - 1] + cost,  # Cost of substitutions
            )

    ratio = ((len(s) + len(t)) - distance[row][col]) / (len(s) + len(t))
    return ratio


def load_json(
    filepath: str, *, make_keys_int=False
) -> Union[Dict[str, VALID_JSON_TYPES], List[VALID_JSON_TYPES]]:
    """Reads a file and returns the content

    Parameters
    ----------
    filepath : str
        The path to the file to read

    Returns
    -------
    Union[dict, list]
        the content gotten from the file
    """
    with open(filepath) as f:
        data = json.load(f)
        return {int(k): v for k, v in data.items()} if make_keys_int else data


def make_permissions(
    perm_value: Union[int, str], *, oauth_url: int = None
) -> discord.Permissions:
    """Makes a discord.Permissions object from the given value

    Examples
    --------
    >>> make_permissions(8)
    <Permissions value=8>
    >>> make_permissions('none')
    <Permissions value=0>
    >>> make_permissions('all')
    <Permissions value=68719476735>
    >>> make_permissions(8, oauth_url=723234115746398219)
    'https://discord.com/oauth2/authorize?client_id=723234115746398219&scope=bot&permissions=8'
    >>> make_permissions('none', oauth_url=723234115746398219)
    'https://discord.com/oauth2/authorize?client_id=723234115746398219&scope=bot&permissions=0'
    >>> make_permissions('all', oauth_url=723234115746398219)
    'https://discord.com/oauth2/authorize?client_id=723234115746398219&scope=bot&permissions=68719476735'

    Parameters
    ----------
    perm_value : Union[int,str]
        The value to generate the permissions for
    oauth_url : int
        If specified, returns an oauth url for that id

    Returns
    -------
    discord.Permissions
        The permission object that was generated
    """
    perm = (
        discord.Permissions(perm_value)
        if isinstance(perm_value, int)
        else getattr(discord.Permissions, perm_value)
    )
    return discord.utils.oauth_url(oauth_url, perm) if oauth_url else perm


def print_error(error: str) -> None:
    """Prints a error with formatting

    Parameters
    ----------
    error : str
        The error message to display
    """
    # We get the 2nd item in the call stack to find where this function is called from
    frame = inspect.stack()[1]
    # We get the module of the caller
    module = inspect.getmodule(frame[0])
    if module is None:
        filename = "Unknown"
    else:
        # We get the file of the module
        filepath = module.__file__
        # We get the relative file path of the module
        filename = os.path.relpath(filepath)
    # We print the info with some color
    rich.print(f"[bold underline red]ERROR:[/] [blue]({filename})[/] : {error}")


def read_file(filepath: str, *args, **kwargs) -> AnyStr:
    """Reads a file and returns the content

    Parameters
    ----------
    filepath : str
        The path to the file to read

    Returns
    -------
    AnyStr
        the content of the file
    """
    with open(filepath, *args, **kwargs) as f:
        return f.read()


def split_by_slice(data: Iterable[Any], length: int) -> Iterable[Any]:
    """Splits the data given at each given length and returns the splitted data

    Examples
    --------
    >>> split_by_slice([1, 2, 3, 4, 5], 3)
    [[1, 2, 3], [4, 5]]
    >>> split_by_slice([1, 2, 3, 4, 5, 6, 7, 8, 9], 3)
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    Parameters
    ----------
    data : Iterable[Any]
        The data to split
    length : int
        Where the data should be split

    Returns
    -------
    Iterable[Any]
        The splitted data
    """

    result = []

    for i in range(0, len(data), length):
        result.append(data[i : i + length])

    return result


def write_file(filepath: str, content: AnyStr, *args, **kwargs) -> AnyStr:
    """Writes to a file and returns the content

    Parameters
    ----------
    filepath : str
        The path to the file to write to
    content: AnyStr
        The content to write to the file

    Returns
    -------
    AnyStr
        The thing that was written to the file
    """
    with open(filepath, "w" if content is str else "wb", *args, **kwargs) as f:
        f.write(content)
        return content
"""A file for all the classes."""
import json

from discord.ext import commands
from dataclasses import dataclass
from .functions import print_error

__all__ = ('BlackListed', 'CodeStats', 'Config', 'CustomEmojis', 'Map', 'NoAPIKey')

class BlackListed(commands.CheckFailure):
    """Don't respond if the user is blocked from using the bot."""


class NoAPIKey(commands.CheckFailure):
    """The bot owner didn't setup a api key yet."""


@dataclass
class CodeStats:
    """A class to easily manage code statistics"""
    comments: int = 0
    coroutines: int = 0
    characters: int = 0
    functions: int = 0
    classes: int = 0
    lines: int = 0
    strings: int = 0
    filecount: int = 0
    imports: int = 0
    commands: int = 0
    if_: int = 0
    else_: int = 0
    elif_: int = 0
    docstrings: int = 0
    embeds = 0


class Map(dict):
    """A subclass of dict that allows you to use a dot (.) to get items"""

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for key, value in arg.items():
                    if isinstance(value, dict):
                        value = Map(value)
                    if isinstance(value, list):
                        self.__convert(value)
                    self[key] = value

        if kwargs:
            for key, value in kwargs.items():
                if isinstance(value, dict):
                    value = Map(value)
                elif isinstance(value, list):
                    self.__convert(value)
                self[key] = value

    def __convert(self, value):
        for element in range(0, len(value)):
            if isinstance(value[element], dict):
                value[element] = Map(value[element])
            elif isinstance(value[element], list):
                self.__convert(value[element])

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


class Config(Map):
    """A class to handle config stuff"""

    @classmethod
    def from_json(cls, json_data):
        """Initialize a object from json."""
        data = json.loads(json_data)
        return cls(data)


class CustomEmojis(Config):
    """A class to handle custom emojis"""

    # This does not have any code because this should just be a alias to Config.
    # I know there are better ways to make this an alias but this is well enough.

class NoneClass:
    def __init__(self, message):
        self.message = message

    def __getattr__(self, attr):
        print_error(self.message)

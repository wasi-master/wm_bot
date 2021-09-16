"""A cog used for reloading other cogs after they're edited
"""
import datetime
import os
import pathlib

import rich
from discord.ext import commands, tasks
from rich.console import Console
from rich.panel import Panel
from rich.style import Style

# put your extension names in this list
# if you don't want them to be reloaded
IGNORE_EXTENSIONS = ["jishaku", "hotreload"]
console = Console()


def format_exception(exception: Exception, extension: str) -> str:
    return (
        str(exception)
        .split(":", 1)[1]  # We remove the "Extension <name> could not be loaded" part
        .replace(extension.split(".")[-1] + ".py, ", "")  # We remove the file name from the error
        .strip()  # We remove the trailing spaces
    )


def path_from_extension(extension: str) -> pathlib.Path:
    """Returns a path from a given extension

    Parameters
    ----------
    extension : str
        the extension for the path to be gotten form

    Returns
    -------
    pathlib.Path
        the path
    """
    return pathlib.Path(extension.replace(".", os.sep) + ".py")


class HotReload(commands.Cog):
    """Cog for reloading extensions as soon as the file is edited"""

    def __init__(self, bot):
        self.bot = bot
        self.loops = 0
        self.last_modified_time = {}
        self.hot_reload_loop.start()

    def cog_unload(self):
        """Occurs when the cog is unloaded"""
        self.hot_reload_loop.stop()

    @tasks.loop(seconds=3)
    async def hot_reload_loop(self):
        """
        Loops every 3 seconds and checks if any extension has been updated.
        loads the extension if it was updated
        """
        self.loops += 1
        if self.loops == 1:
            # Ignore the first loop since no one is gonna edit a cog just after the bot starts
            return
        for extension in list(self.bot.extensions.keys()):
            if extension in IGNORE_EXTENSIONS:
                continue

            path = path_from_extension(extension)
            time = os.path.getmtime(path)
            try:
                if self.last_modified_time[extension] == time:
                    continue
            except KeyError:
                self.last_modified_time[extension] = time

            try:
                self.bot.reload_extension(extension)
            except commands.ExtensionNotLoaded:
                continue
            except commands.ExtensionError as exception:
                rich.print(
                    Panel(
                        f"[#ff0000]Couldn't reload extension:[/] [bold yellow]{extension}[/]\n[cyan]{format_exception(exception, extension)}[/]",
                        title=f"Hot Reloading Failed - {datetime.datetime.now()}",
                        style=Style(bgcolor="#600000"),
                    )
                )
            else:
                rich.print(
                    Panel(
                        f"[green]Reloaded extension:[/] [bold yellow]{extension}[/]",
                        title=f"Hot Reloading Success - {datetime.datetime.now()}",
                        style=Style(bgcolor="dark_green"),
                    )
                )
            finally:
                self.last_modified_time[extension] = time

    @hot_reload_loop.before_loop
    async def cache_last_modified_time(self):
        """Saves the last modified time of an extension"""
        self.last_modified_time = {}
        # Mapping = {extension: timestamp}
        for extension in self.bot.extensions.keys():
            if extension in IGNORE_EXTENSIONS:
                continue
            path = path_from_extension(extension)
            time = os.path.getmtime(path)
            self.last_modified_time[extension] = time


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(HotReload(bot))

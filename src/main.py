"""Main file."""
import logging
import os

import discord
from discord.ext import commands
from playsound import PlaysoundException, playsound
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import track

from utils.bot import WMBot, create_db_pool

blacklisted_extensions = ["abandoned.py"]
initial_extensions = [
    "extensions." + file[:-3]
    for file in os.listdir("extensions/")
    if file.endswith(".py")
    if not file in blacklisted_extensions
]

bot = WMBot()
console = Console()
logging.basicConfig(level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])


async def on_ready():
    """Fires when the bot goes online"""
    # We use this so that this event only fires after the bot is ready
    await bot.wait_until_ready()

    # We try to play a sound to let the user know that the bot is online
    # If the sound playing fails we just ignore it
    try:
        playsound("assets/sounds/connected_to_discord.mp3", block=False)
    except PlaysoundException:
        pass

    # We print bot is online to the console
    console.print("[green]Bot is online[/]")

    # We load jishaku, this is a good cog to have
    bot.load_extension("jishaku")
    # We load our hot reloading cog. This will reload cogs as we edit them in real time
    bot.load_extension("hotreload")

    # We loop through all the extensions and load them.
    # If there is a error we print it to the console and add the cog name to unloaded
    unloaded = []
    for extension in track(initial_extensions, description="[yellow]Loading Cogs[/]"):
        try:
            bot.load_extension(extension)
        except commands.ExtensionFailed as exc:
            unloaded.append(extension.split(".")[-1])
            console.print_exception()

    # If there are errors, then we send a message to the user notifying them
    if unloaded:
        await bot.owner.send(
            f"Couldn't load {len(unloaded)}/{len(initial_extensions)} cogs ({', '.join(unloaded)}). Check the console for details."
        )

    # We send the bot ready message to the bot owner, just in case
    # if the user is not looking at the terminal but is in discord
    await bot.owner.send(f"Bot ready")

    # We try to play a sound to let the user know that the bot is online
    # If the sound playing fails we just ignore it
    try:
        playsound("assets/sounds/bot_online.mp3", block=False)
    except PlaysoundException:
        pass

    # We add a final print to say that all the cogs have been loaded
    console.print("[green]All cogs loaded[/]")


if __name__ == "__main__":
    bot.loop.run_until_complete(create_db_pool(bot))
    bot.loop.create_task(on_ready())
    try:
        bot.run(os.environ["token"])
    except KeyboardInterrupt:
        console.print("[red]Bot Closing[/]")
    except discord.PrivilegedIntentsRequired:
        console.print(
            "[red]Go to [/][blue]https://discord.com/developers/applications/[/][red] and enable the intents that are required. Currently these are as follows:[/]"
        )
    except discord.LoginFailure:
        console.print("[red]The token is most likely incorrect[/]")
    except discord.ConnectionClosed as e:
        console.print(f"[red]Connection closed[/][yellow]Code: {e.code} Reason: {e.reason}[/]")
    except discord.HTTPException as e:
        console.print("[red]Could not connect to discord.com ({e.status} {e.code}: {e.text})[/]")
    except KeyError:
        console.print("[red]No token found in the environment variables[/]")
    except discord.GatewayNotFound:
        console.print("[red]The API is probably having an outage,[/] [blue]see https://discordstatus.com[/]")
    except Exception as e:
        raise e

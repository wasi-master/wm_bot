import argparse
import asyncio
import json
import logging
import re
from difflib import get_close_matches

import aiohttp
import discord
import rich
from cli import parser
from emojis import EMOJIS_JSON
from rich.logging import RichHandler
from rich.progress import Progress

# You should not change these
ITEM_REGEX = r"\"(?P<key>\w+)\": \"(?P<emoji><a?:[a-zA-Z0-9_]{2,32}:[0-9]{18,22}>)\""
EMOJI_REGEX = r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>"
EMOJI_FORMAT = "https://cdn.discordapp.com/emojis/{}.png?"

# You can also change these but it's not recommended unless you know what you're doing
LOGGING_FORMAT = "%(message)s"
LOGGING_LEVEL = logging.WARNING

args = parser.parse_args()
console = rich.console.Console()
rprint = console.print
rinput = console.input


logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT, datefmt="[%X]", handlers=[RichHandler()])
client = discord.Client(intents=discord.Intents.default())
# We create the client

if not args.token:
    TOKEN = rinput("[bold yellow]Enter your token:[/] ")
    rprint("[green]Logging in with token[/]")
else:
    TOKEN = args.token

LOGGING_LEVEL = logging.DEBUG if args.debug else LOGGING_LEVEL
GUILD_ID = None


def end():
    try:
        exit()
    except SystemExit:
        pass


@client.event
async def on_ready():
    global GUILD_ID
    if not args.guild_id:
        while True:
            gid = rinput("[bold cyan]Enter the server ID or name:[/] ")
            if gid.isdigit():
                GUILD_ID = int(gid)
                break

            if not re.match(r"[\w\d\s.-'\"]+", gid):
                rprint("[red]Invalid ID or name[/]")
                continue

            guild = discord.utils.get(client.guilds, name=gid)
            if not guild:
                guild = discord.utils.find(lambda candidate: candidate.name.lower() == gid.lower(), client.guilds)

            if not guild:
                possible_guilds = get_close_matches(gid, [g.name for g in client.guilds])
                rprint(
                    "[orange]Server not found, did you mean one of these?\n" + "\n".join(possible_guilds) + "[/]"
                )
                continue

            GUILD_ID = guild.id
            break

    client.loop.create_task(main())


async def main():
    """The main function."""
    session = aiohttp.ClientSession()

    await client.wait_until_ready()
    guild = client.get_guild(GUILD_ID)
    if not guild:
        rprint("[red]No guild found[/]")
        logging.error("No guild found")
        end()
    with Progress() as progress:
        process = progress.add_task("[cyan]Processing...", total=32)
        download = progress.add_task("[red]Downloading...", total=32)
        add = progress.add_task("[green]Adding...", total=32)

        emojis_data = json.loads(EMOJIS_JSON)

        async def process_node(node):
            if isinstance(node, dict):
                result = {}
                for key, value in node.items():
                    progress.update(process, advance=1)
                    if isinstance(value, str):
                        emoji_match = re.fullmatch(EMOJI_REGEX, value)
                        if emoji_match:
                            _, name, emoji_id = emoji_match.groups()
                            already_added = discord.utils.get(guild.emojis, name=key)
                            if already_added:
                                emoji = already_added
                                progress.update(download, advance=1)
                            else:
                                emoji_url = EMOJI_FORMAT.format(emoji_id)
                                progress.update(download, advance=1)
                                async with session.get(emoji_url) as resp:
                                    data = await resp.read()
                                    progress.update(add, advance=1)
                                    emoji = await guild.create_custom_emoji(
                                        name=key,
                                        image=data,
                                        reason=f"Created by emoji_adder.py (Original emoji: {name})",
                                    )
                            result[key] = str(emoji)
                            continue
                    result[key] = await process_node(value)
                return result

            if isinstance(node, list):
                return [await process_node(value) for value in node]

            return node

        emojis_data = await process_node(emojis_data)
        progress.stop()

    try:
        await session.close()
        await client.close()
    except RuntimeError:
        pass

    rprint(json.dumps(emojis_data, indent=4))

    try:
        exit()
    except SystemExit:
        rprint("[bold green]Done![/]")


try:
    client.run(TOKEN)
except discord.LoginFailure:
    rprint("[red]Login failed, maybe an invalid token was passed?[/]")

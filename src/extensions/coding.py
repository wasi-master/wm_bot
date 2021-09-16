import asyncio
import difflib
import inspect
import json
import re
from datetime import datetime
from html import unescape
from json import JSONDecodeError
from urllib.parse import quote

import discord
import humanize
from attrdict import AttrDict
from bs4 import BeautifulSoup
from discord.ext import commands
from rich import print as rprint

from utils.functions import split_by_slice
from utils.paginator import Paginator


def parse_pypi_index(text):
    """Parses the text and returns all the packages

    Parameters
    ----------
    text : str
        the html of the website (https://pypi.org/simple/)

    Returns
    -------
    List[str]
        the list of packages
    """
    soup = BeautifulSoup(text, "lxml")
    return [i.get_text() for i in soup.find_all("a")]


class Coding(commands.Cog):
    """Commands releated to Programming"""

    def __init__(self, bot):
        self.bot = bot
        # Setting up our pypi index
        self.pypi_index = []
        bot.loop.create_task(self.get_pypi_packages())

    async def get_pypi_packages(self):
        """Gets the pypi packages from the index and saves them"""
        async with self.bot.session.get("https://pypi.org/simple/") as r:
            resp = await r.text()
            self.pypi_index = await self.bot.loop.run_in_executor(None, parse_pypi_index, resp)
        rprint(f"[green]Loaded[/] [yellow]{len(self.pypi_index):,}[/] [green]pypi packages[/]")

    @commands.command(name="regex", extras={"image": "https://i.imgur.com/Tab4FUF.gif"})
    async def _regex(self, ctx, regex, text):
        """Matches text to the regex provided"""
        try:

            # We wrap it inside a executor so it doesn't block the event loop.
            task = self.bot.loop.run_in_executor(None, re.search, regex, text)
            # We use timeout=10 so if the search takes more than 10 seconds a TimeoutError is raised.
            match = await asyncio.wait_for(task, timeout=10)

        # This will happen if the search takes more than 10 seconds.
        except asyncio.TimeoutError:
            return await ctx.send("Regex timed out")
        else:
            if match:
                await ctx.send(f"**Regex:** ```{regex}``` **Match:** ```{text[match.start():match.end()]}```")
            else:
                await ctx.send("No match")

    @commands.command(name="json", extras={"image": "https://i.imgur.com/vsABmqr.gif"})
    async def _json(self, ctx, *, json_string):
        """Formats the given json string"""
        json_string = json_string.lstrip("```").rstrip("```").lstrip("json")
        # if the data is not really json but is like python dict/list we replace the stuff
        replacements = {"'": '"', "False": "false", "True": "true", "None": "null"}
        for to_replace, replacement in replacements.items():
            json_string = json_string.replace(to_replace, replacement)
        try:
            parsed_json = json.loads(json_string)
        except JSONDecodeError as error:
            await ctx.send(
                embed=discord.Embed(
                    title="Invalid JSON",
                    description=discord.utils.escape_markdown(json_string),
                    color=0xFF0000,
                ).add_field(name="Exception", value=error)
            )
        else:
            pretty_json = json.dumps(parsed_json, indent=4)
            await ctx.send(f"```json\n{pretty_json}```")

    @commands.command(name="diff", aliases=["difference", "dif"])
    async def difference(self, ctx, first, second):
        """Sends the unified todifference between first and second
        Note: if the text is small or the difference is not very large you should use the `ndiff` command"""
        # WE split the lines by newline characters
        first_lines = first.splitlines()
        second_lines = second.splitlines()
        # We get the unified difference
        diff = difflib.unified_diff(first_lines, second_lines, fromfile="first", tofile="second")
        # We send the unified difference
        if diff:
            await ctx.send("```diff\n" + "\n".join(diff) + "```")
        else:
            await ctx.send("No difference found")

    @commands.command(name="ndiff", aliases=["ndifference", "ndif"])
    async def ndifference(self, ctx, first, second):
        """Sends the only difference between first and second
        Note: there is another diff command that can be used instead for
        large texts and difference between multiple lines"""
        # We split the text by new lines
        first_lines = first.splitlines()
        second_lines = second.splitlines()
        # We get the difference
        diff = difflib.ndiff(first_lines, second_lines)
        # We send the differences
        if diff:
            await ctx.send("```diff\n" + "\n".join(diff) + "```")
        else:
            await ctx.send("No difference found")

    @commands.group(aliases=["so"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stackoverflow(self, ctx):
        ...

    @stackoverflow.command(name="tag", aliases=["t"])
    @commands.bot_has_permissions(use_external_emojis=True)
    async def stackoverflow_tag(self, ctx, tag_name):
        """Shows up to 30 recent questions for a tag on stackoverflow"""
        url = f"https://api.stackexchange.com/2.3/questions"

        params = {
            "order": "desc",
            "sort": "activity",
            "tagged": tag_name,
            "site": "stackoverflow",
            "filter": "!6VvPDzPz(cfXL",
        }

        async with self.bot.session.get(url, params=params) as response:
            data = AttrDict(await response.json())
        if len(data.items) == 0:
            return await ctx.send("No results found")

        embeds = []
        for item in data.items:
            embed = discord.Embed(title=item.title, url=item.link, color=0xC75E0D)
            description = unescape(item.body_markdown)
            embed.description = description if len(description) < 2048 else "Description too long"
            embed.set_author(
                name=f"{item.owner.display_name} ({item.owner.reputation} Reputation)",
                icon_url=item.owner.profile_image,
                url=item.owner.link,
            )
            embed.add_field(
                name="Stats",
                value=f'🗯️ Tags: {", ".join(item.tags)}\n'
                f"👀 Views: {item.view_count}\n"
                f"📰 Answer Count: {item.answer_count}\n"
                f"⬆️ Score: {item.score}\n" + ("✅ Answered\n" if item.is_answered else "❌ Not Answered\n"),
            )
            if item.answers_count != 0 and item.answers is not None:
                embed.add_field(
                    name="Answers",
                    value="\n".join(
                        f"{'✅ Accepted ' if answer.is_accepted else ''}[{answer.owner.display_name}]({answer.owner.link}): [click here](https://stackoverflow.com/a/{answer.answer_id}) ({answer.score} Score)"
                        for answer in item.answers
                    ),
                )
            embeds.append(embed)

        pag = Paginator(embeds)
        await pag.start(ctx)

    @stackoverflow.command(name="search", aliases=["s"])
    @commands.bot_has_permissions(use_external_emojis=True)
    async def stackoverflow_search(self, ctx, *, query):
        return await ctx.send("WIP")
        # using https://api.stackexchange.com/docs/advanced-search
        url = f"https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=activity&title={quote(query)}&site=stackoverflow"
        async with self.bot.session.get(url) as response:
            data = AttrDict(await response.json())
        if len(data.items) == 0:
            return await ctx.send("No results found")
        embeds = []
        for item in data.items:
            embed = discord.Embed(title=item.title, url=item.link, color=0xC75E0D)
            embed.description = (
                f'Tags: {", ".join(item.tags)}\n'
                f"Views: {item.view_count}\n"
                f"Answer Count: {item.answer_count}\n"
                f"Score: {item.score}\n"
                f"✅ Answered\n"
                if item.is_answered
                else "❌ Not Answered\n"
            )
            embed.set_author(
                name=f"{item.owner.display_name} ({item.owner.reputation} Reputation)",
                icon_url=item.owner.profile_image,
                url=item.owner.link,
            )
            embeds.append(embed)
        pag = Paginator(embeds)
        await pag.start(ctx)

    @commands.command(
        name="pypi",
        aliases=["pypl", "pip"],
        extras={"image": "https://i.imgur.com/5MdrujN.gif"},
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def python_package(self, ctx, package_name: str):
        """Gets information about the specified pypi package"""

        url = f"https://pypi.org/pypi/{package_name}/json"
        async with self.bot.session.get(url) as response:
            if response.status == 404:
                return await ctx.send("Project not found")
            if response.status != 200:
                return await ctx.send(f"Some error occured. response code {response.status}")
            parsed_json = json.loads(await response.text())

        stats_url = f"https://pypistats.org/api/packages/{package_name}/recent"
        async with self.bot.session.get(stats_url) as r:
            resp = await r.text()
            try:
                parsed_stats = json.loads(resp)
            except json.JSONDecodeError:
                parsed_stats = None

        parsed_json = parsed_json["info"]
        if len(parsed_json["summary"]) != 0:
            embed = discord.Embed(
                title=parsed_json["name"],
                description=parsed_json["summary"].replace("![", "[").replace("]", ""),
                color=0x346C99,  # Python color
            )
        else:
            embed = discord.Embed(title=parsed_json["name"], color=0x346C99)
        if len(parsed_json["author_email"]) == 0:
            email = "None"
        else:
            email = parsed_json["author_email"]
        embed.add_field(name="Author", value=f"Name: {parsed_json['author']}\nEmail: {email}")
        embed.add_field(name="Latest Version", value=parsed_json["version"])
        # embed.add_field(name="Summary", value=fj["summary"])
        hp = (
            "Github Repo"
            if re.match(
                r"https://(www\.)?github\.com/[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}/[A-Za-z-]{0,100}",
                parsed_json["home_page"],
            )
            else "Home Page"
        )
        if hp == "Home Page":
            hp = (
                "Github Profile"
                if re.match(
                    r"https://(www\.)?github\.com/[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}/?", parsed_json["home_page"]
                )
                else hp
            )
        embed.add_field(
            name="Links",
            value=f"[{hp}]({parsed_json['home_page']})\n[Project Link]({parsed_json['project_url']})\n[Release Link]({parsed_json['release_url']})",
        )
        if parsed_json["license"] is None or len(parsed_json["license"]) < 3:
            license = "Not Specified"
        else:
            license = parsed_json["license"].replace("{", "").replace("}", "").replace("'", "")
        embed.add_field(name="License", value=f"‌{license}")
        if not parsed_json["requires_dist"] is None:
            if len(parsed_json["requires_dist"]) > 5:
                embed.add_field(
                    name=f"Dependencies ({len(parsed_json['requires_dist'])})",
                    value=", ".join([f"`{i.split()[0]}`" for i in parsed_json["requires_dist"]]),
                    inline=False,
                )
            elif len(parsed_json["requires_dist"]) > 15:
                embed.add_field(name="Dependencies", value=len(parsed_json["requires_dist"]))
            elif len(parsed_json["requires_dist"]) != 0:
                embed.add_field(
                    name=f"Dependencies ({len(parsed_json['requires_dist'])})",
                    value="\n".join([i.split(" ")[0] for i in parsed_json["requires_dist"]]),
                    inline=False,
                )
        if not parsed_json["requires_python"] is None:
            if len(parsed_json["requires_python"]) > 2:
                python_emoji = self.bot.emoji_config.other.python
                embed.add_field(
                    name=f"{python_emoji} Python Version Required",
                    value=parsed_json["requires_python"],
                )
        if parsed_stats is not None and parsed_stats != 404:
            embed.add_field(
                name="Downloads",
                value=f"```prolog\nLast Day: {parsed_stats['data']['last_day']:,}\nLast Week: {parsed_stats['data']['last_week']:,}\nLast Month: {parsed_stats['data']['last_month']:,}```",
                inline=False,
            )
        await ctx.send(embed=embed)

    @commands.command(
        aliases=["pypi-search", "pipsearch", "pypis", "pips"],
        extras={"image": "https://i.imgur.com/xQK85rO.gif"},
    )
    # @commands.max_concurrency(1, commands.BucketType.default)
    @commands.bot_has_permissions(use_external_emojis=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pypi_search(self, ctx, package_search):
        """Searches pypi andreturns top 100 results"""
        if not self.pypi_index:
            message = await ctx.send("Not ready yet. Please try again in a few seconds.")

        matches = difflib.get_close_matches(package_search, self.pypi_index, n=100, cutoff=0.5)
        embeds = []
        i = 0
        for package_list in split_by_slice(matches, 10):
            embed = discord.Embed(title=f"Python Packages matching {package_search}", description="")
            for package in package_list:
                i += 1
                embed.description += f'{i}. [{package}](https://pypi.org/pypi/{package} "{package}")\n'
            embed.description += (
                "\n\nSend a package name in 20 seconds and I will show more details about that package."
            )
            embeds.append(embed)
        menu = Paginator(embeds)
        await menu.start(ctx)
        try:
            message = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.content.lower() in matches,
                timeout=120,
            )
        except asyncio.TimeoutError:
            return
        else:
            ctx.message = message
            await self.python_package(ctx, message.content)

    @commands.command(
        name="crates",
        description="Searches crates for rust packages",
        aliases=["crt", "cargo"],
    )
    async def rust_package(self, ctx, package_name: str):

        url = f"https://crates.io/api/v1/crates/{package_name}"
        async with self.bot.session.get(url) as response:
            if '"detail": "Not Found"' in await response.text():
                return await ctx.send("Project not found")
            else:
                fj = json.loads(await response.text())
        oj = fj
        fj = fj["crate"]
        if len(fj["description"]) != 0:
            embed = discord.Embed(
                title=fj["name"],
                description=fj["description"].replace("![", "[").replace("]", ""),
                color=0x000001,  # Rust color, not exactly black because of some issues
            )
        else:
            embed = discord.Embed(title=fj["name"], color=0x000000)
        embed.add_field(name="Latest Version", value=fj["newest_version"])
        # embed.add_field(name="Summary", value=fj["summary"])
        embed.add_field(
            name="Links",
            value=f"[Home Page]({fj['homepage']})\n[Github Repo]({fj['repository']})\n[Documentation]({fj['documentation']})",
        )
        created_at = datetime.strptime(fj["created_at"][:-9], "%Y-%m-%dT%H:%M:%S.%f")
        embed.add_field(
            name="Added at",
            value=f'{created_at.strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.utcnow() - created_at)})',
        )
        if oj["keywords"]:
            embed.add_field(
                name="Keywords/Tags",
                value="\n".join(f"`{i['id']}` (`{i['crates_cnt']}` crates)" for i in oj["keywords"]),
                inline=False,
            )
        if oj["categories"]:
            embed.add_field(
                name="Categories",
                value="\n".join(f"`{i['category']}` (`{i['crates_cnt']}` crates)" for i in oj["categories"]),
                inline=False,
            )
        await ctx.send(embed=embed)
        embed.add_field(
            name="Downloads",
            value=f"```prolog\nTotal Downloads: {fj['downloads']:,}\nRecent Downloads: {fj['recent_downloads']:,}```",
        )

    @commands.command(
        name="rubygem",
        aliases=["gem", "rg"],
    )
    async def ruby_package(self, ctx, package_name: str):
        """Searches rubygems for ruby packages"""
        async with self.bot.session.get(f"https://rubygems.org/api/v1/versions/{package_name}.json") as response:
            if "This rubygem could not be found." in await response.text():
                return await ctx.send("Project not found.")
            versions = json.loads(await response.text())
            version = versions[0]
        num = version["number"]
        url = f"https://rubygems.org/api/v2/rubygems/{package_name}/versions/{num}.json"
        async with self.bot.session.get(url) as response:
            fj = json.loads(await response.text())
        if len(fj["description"]) != 0:
            embed = discord.Embed(
                title=fj["name"],
                description=fj["description"].replace("![", "[").replace("]", ""),
                color=0xA12712,  # Ruby color
            )
        else:
            embed = discord.Embed(title=fj["name"], color=0xA12712)
        embed.add_field(name="Latest Version", value=fj["version"])
        # embed.add_field(name="Summary", value=fj["summary"])
        embed.add_field(name="Author", value=f"Name: {fj['authors']}")
        embed.add_field(
            name="Links",
            value=f"[Home Page]({fj['homepage_uri']})\n[Github Repo]({fj['source_code_uri']})\n[Documentation]({fj['documentation_uri']})\n[Project]({fj['project_uri']})",
        )
        embed.add_field(
            name="Downloads",
            value=f"Total Downloads: {fj['downloads']:,}\nLatest Version Downloads: {fj['version_downloads']:,}",
        )
        if not fj["dependencies"]["runtime"] is None:
            if len(fj["dependencies"]["runtime"]) > 15:
                embed.add_field(name="Dependencies", value=len(fj["requires_dist"]))
            elif len(fj["dependencies"]["runtime"]) != 0:
                embed.add_field(
                    name=f"Dependencies ({len(fj['dependencies']['runtime'])})",
                    value="\n".join([i["name"] + i["requirements"] for i in fj["dependencies"]["runtime"]]),
                    inline=False,
                )
        embed.add_field(name="Summary", value=fj["summary"])
        created_at = datetime.strptime(fj["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        embed.add_field(
            name="Added at",
            value=f'{created_at.strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.utcnow() - created_at)})',
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["gh"])
    async def github(self, ctx, repo):
        """Shows information about a GitHub repository"""
        url = f"https://api.github.com/repos/{repo}"
        async with self.bot.session.get(url) as response:
            if response.status != 200:
                return await ctx.send("Could not find repo.")
            # We wrap it inside a AttrDict so we can use dot notation
            data = AttrDict(await response.json())
        embed = discord.Embed(title=data.full_name, description=data.description, url=data.html_url)
        embed.set_author(name=data.owner.login, icon_url=data.owner.avatar_url)
        if data.license and data.license.name:
            embed.add_field(name="License", value=data.license.name)
        desc = "\n\n"
        desc += f"🌍 **Language:** {data.language}\n" if data.language else ""
        desc += f"⭐ **Stargazers:** {data.stargazers_count}\n"
        desc += f"👀 **Watchers:** {data.watchers}\n"
        desc += f"🍴 **Forks:** {data.forks_count}\n"
        desc += f"❔ **Open Issues:** {data.open_issues}\n"
        desc += f"🏠 **Home Page:** {data.homepage}\n" if data.homepage else ""
        embed.description += desc
        await ctx.send(embed=embed)

    @commands.command(name="npm")
    async def node_package(self, ctx, package_name: str):
        """Searches npm for node.js packages"""
        url = f"https://registry.npmjs.org/{package_name}"
        async with self.bot.session.get(url) as response:
            if '{"error":"Not found"}' in await response.text():
                return await ctx.send("Project not found")
            else:
                fj = json.loads(await response.text())
        if len(fj["description"]) != 0:
            embed = discord.Embed(
                title=fj["_id"],
                description=fj["description"].replace("![", "[").replace("]", ""),
                color=0xFF0000,  # npmjs color
            )
        else:
            embed = discord.Embed(title=fj["_id"], color=0xFF0000)
        # author = fj.get("author")
        # embed.add_field(
        #     name="Author",
        #     value=f"Name: [{author.get('name')}]({author.get('url', 'None')})\nEmail: {author.get('email')}",
        #     inline=False,
        # )
        latest_ver = sorted(fj["versions"])[-1]
        embed.add_field(name="Version", value=latest_ver)
        main = ""
        for num, maintainer in enumerate(fj["maintainers"], start=1):
            author = maintainer
            main += f"‌    **{num}.** Name: [{author.get('name')}]({author.get('url', 'None')})\n‌        Email: {author.get('email')}\n\n"
        embed.add_field(name="Maintainers:", value=main, inline=False)
        links = []
        if fj.get("homepage"):
            links.append(f'[Home Page]({fj["homepage"]})')
        if fj.get("bugs"):
            links.append(f'[Bug Tracker]({fj["bugs"]["url"]})')
        github = fj["repository"]["url"][4:-4]
        links.append(f"[Github Repo]({github})")
        links.append(f"[Package Link]({'https://www.npmjs.com/package/'+fj['_id']})")
        embed.add_field(name="Links", value="\n".join(links))
        if fj.get("license"):
            embed.add_field(name="License", value=fj["license"])
        dependencies = list(fj["versions"][latest_ver]["dependencies"])
        if dependencies:
            if len(dependencies) > 15:
                embed.add_field(name="Dependencies", value=len(dependencies), inline=False)
            elif len(dependencies) > 7:
                embed.add_field(name="Dependencies", value=", ".join(dependencies))
            else:
                embed.add_field(name="Dependencies", value="\n".join(dependencies))
        await ctx.send(embed=embed)

    @commands.command()
    async def rtfs(self, ctx, search):
        """
        Gets the source for an object from the discord.py library
        """
        overhead = ""
        raw_search = search
        searches = []
        if "." in search:
            searches = search.split(".")
            search = searches[0]
            searches = searches[1:]
        get = getattr(discord, search, None)
        if get is None:
            get = getattr(commands, search, None)
            if get is None:
                get = getattr(discord.ext.tasks, search, None)
        if get is None:
            return await ctx.send(f"Nothing found under `{raw_search}`")
        if inspect.isclass(get) or searches:
            if searches:
                for i in searches:
                    last_get = get
                    get = getattr(get, i, None)
                    if get is None and last_get is None:
                        return await ctx.send(f"Nothing found under `{raw_search}`")
                    elif get is None:
                        overhead = f"Couldn't find `{i}` under `{last_get.__name__}`, showing source for `{last_get.__name__}`\n\n"
                        get = last_get
                        break
        if isinstance(get, property):
            get = get.fget

        lines, firstlineno = inspect.getsourcelines(get)
        try:
            module = get.__module__
            location = module.replace(".", "/") + ".py"
        except AttributeError:
            location = get.__name__.replace(".", "/") + ".py"

        ret = f"https://github.com/Rapptz/discord.py/blob/v{discord.__version__}"
        final = f"{overhead}[{location}]({ret}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1})"
        await ctx.send(embed=discord.Embed(description=final))


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Coding(bot))

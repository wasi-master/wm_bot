import difflib
import os
import re
from utils.error_formatter.collector import Report
import aiohttp
import discord
from discord.ext import commands

try:
    import rich
    from rich.traceback import Traceback

    HAS_RICH = True
except ImportError:
    HAS_RICH = False
from utils.functions import format_name, print_error
from utils.classes import BlackListed
from utils.error_formatter import HTMLFormatter, TextFormatter, Report



class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The Error Handler."""
        # If the command has a local error handler then we return to not handle errors here
        if hasattr(ctx.command, "on_error"):
            return
        # When an exception is raised on command invoke, it gets wrapped in CommandInvokeError
        # before being thrown to an error handler . we use this to safely unwrap it:
        error = getattr(error, "original", error)
        # If the users uses a command that doesn't exist we notify the user
        if isinstance(error, commands.CommandNotFound):
            # We get what the user used
            invoked_with = ctx.message.content.replace(ctx.prefix, "")
            # We know none of our commands are over 25 characters so we send
            # this message to avoid people spamming with long texts
            if len(invoked_with) > 25:
                return await ctx.send("That command does not exist")
            # We make a list of all commands aliases and names
            _commands = []
            for command in self.bot.commands:
                if command.aliases:
                    for alias in command.aliases:
                        _commands.append(alias)
                _commands.append(command.name)
            # We get the simillar commands and validate it
            cmds = difflib.get_close_matches(invoked_with, _commands, cutoff=0.4)
            if not cmds:
                return await ctx.send("Invalid command used, there are no commands that are simillar")
            # We send the possible commands to the user
            await ctx.send(
                embed=discord.Embed(
                    title=f"Command {invoked_with} not found",
                    description="Did you mean?\n"
                    + "\n".join([f"**{index}.**  {command}" for index, command in enumerate(cmds, start=1)]),
                )
            )
        elif isinstance(error, BlackListed):
            # If the dude is blacklisted for some reason, we just ignore them
            return
        if isinstance(error, commands.MissingPermissions):
            # If the user does not have the sufficient permissions then we send a message
            missing_perms = ", ".join(format_name(perm) for perm in error.missing_permissions)
            await ctx.send(f"You don't have the permission ({missing_perms}) to use {ctx.command} command")
        elif isinstance(error, commands.MissingRequiredArgument):
            # If any argument is missing then we send some stuff
            # We first get the command signature
            signature = ctx.prefix + ctx.invoked_with + " " + ctx.command.signature
            # We get the missing argument
            invalid_arg_original = error.param.name
            # we save the missing argument for some work later
            invalid_arg = invalid_arg_original
            # sometimes the argument has _ to seperate words in the name, like search_term.
            # since python does not allow there to be spaces in the name, we replace them with _
            # and here we remove that _ to make the argument to be more user friendly
            if "_" in invalid_arg:
                invalid_arg = invalid_arg.replace("_", " ")
            # https://docs.python.org/3/library/stdtypes.html#str.title
            invalid_arg = invalid_arg.title()
            # we replace the original signature witht the argument to be more user friendly
            # like, `wm,help [command_name]` becomes `wm,help [Command Name]`
            signature = signature.replace(invalid_arg_original, invalid_arg)
            # now we format the error message, we use ```ml to make it colorized
            error_message = "```ml\n"
            error_message += signature + "\n"
            error_message += " " * signature.index(invalid_arg) + " " * round(len(invalid_arg) / 2) + "^\n"
            error_message += f"SyntaxError: the required argument {invalid_arg} is missing```"
            # and now we send
            await ctx.send(embed=discord.Embed(title="Missing Argument", description=error_message))
        elif isinstance(error, commands.TooManyArguments):
            # since the user provided a argument that is not needed, the signature
            # won't work like above, so we just get the message content
            signature = ctx.message.content
            # now we get the last word that the user used, this is the  unnecessary argument
            invalid_arg = ctx.message.content.split()[-1]
            # Now we format the error message
            error_message = "```ml\n"
            error_message += signature + "\n"
            error_message += " " * signature.index(invalid_arg) + " " * round(len(invalid_arg) / 2) + "^\n"
            error_message += f"SyntaxError: the argument {invalid_arg} is not required but was passed```"
            # Now we send the message
            await ctx.send(embed=discord.Embed(title="Too Many Arguments", description=error_message))
        elif isinstance(error, commands.BadArgument):
            error_regex = r"Converting to \"(?P<type>\w+)\" failed for parameter \"(?P<param>\w+)\"[\.:](?P<message>[a-zA-Z-_\".]+)?"
            error_match = re.search(error_regex, str(error))
            if error_match is None:
                # It will be none for custom converters that don't use this format
                await ctx.send(str(error))
            arg_type, arg = error_match.group("type", "param")
            # We get the error message from the error
            message = None
            if hasattr(error, "__cause__"):
                # If the eror has a cause, then we use that cause as the message
                message = str(error.__cause__)
            elif error.group("message"):
                # else if there are text after the error, we use that as the message
                message = error.group("message")

            # If any argument is invalid then we send some stuff
            # We first get the command signature
            signature = ctx.prefix + ctx.invoked_with + " " + ctx.command.signature
            # We get the invalid argument
            invalid_arg_original = arg
            # we save the invalid argument for some work later
            invalid_arg = invalid_arg_original
            # sometimes the argument has _ to seperate words in the name, like search_term.
            # since python does not allow there to be spaces in the name, we replace them with _
            # and here we remove that _ to make the argument to be more user friendly
            if "_" in invalid_arg:
                invalid_arg = invalid_arg.replace("_", " ")
            # https://docs.python.org/3/library/stdtypes.html#str.title
            invalid_arg = invalid_arg.title()
            # we replace the original signature witht the argument to be more user friendly
            # like, `wm,help [command_name]` becomes `wm,help [Command Name]`
            signature = signature.replace(invalid_arg_original, invalid_arg)
            # now we format the error message, we use ```ml to make it colorized
            error_message = "```ml\n"
            error_message += signature + "\n"
            error_message += " " * signature.index(invalid_arg) + " " * round(len(invalid_arg) / 2) + "^\n"
            error_message += f"SyntaxError: the argument {invalid_arg} is not valid\n"
            if message:
                error_message += f"Reason: {message}```"
            # and now we send
            await ctx.send(embed=discord.Embed(title="Invalid Argument", description=error_message))
        elif isinstance(error, discord.NotFound):
            # If the user provided a item that was not found or does not exist, then we send a message
            await ctx.send(embed=discord.Embed(title="Not Found", description=str(error)))
        elif isinstance(error, commands.BotMissingPermissions):
            # If the bot does not have permissions to do something, then we send a message
            missing_perms = ", ".join(format_name(perm) for perm in error.missing_permissions)
            await ctx.send(f"The bot does not have the permission ({missing_perms}) to execute this command")
        elif isinstance(error, discord.HTTPException):
            # This error is thrown when an HTTP request operation fails
            if error.code == 50007:
                # This code is used when the user blocked us therefore we can't dm them
                return await ctx.send("Do not block bot 😠")
            # If it is another error then we just send the error code and the usual cause of the code
            await ctx.send(
                f"Something was wrong with the request, the response I got was: "
                f"{self.bot.httpexception_codes[error.code]} ({error.code})"
            )
        elif isinstance(error, commands.CommandOnCooldown):
            # If the command is on cooldown then we send a message
            embed = discord.Embed(
                title="Slow Down!",
                description=(
                    f"The command `{ctx.command}` is on cooldown, "
                    f"please try again after **{round(error.retry_after, 2)}** seconds.\n"
                    "Patience, patience."
                ),
                colour=0xFF0000,
            )
            await ctx.send(embed=embed)
        else:
            # If we are running tests then we just raise the error
            if os.environ.get("RUNNING_WMBOT_TESTS"):
                raise error
            # We make a collector
            report = Report.from_exception(error)

            # We make a html and a text formatter
            html = HTMLFormatter().format(report)
            text = TextFormatter().format(report)

            # We save the traceback to files
            with open(f"errors/error_{report.timestamp}.html", "wb") as f:
                f.write(html)
            with open(f"errors/error_{report.timestamp}.txt", "w", encoding="utf-8") as f:
                f.write(text)

            # We upload the text to the cloud
            req = await self.bot.session.post("https://hastebin.com/documents", data=text)
            reqjson = None
            try:
                reqjson = await req.json()
                key = reqjson["key"]
            except (KeyError, aiohttp.ContentTypeError):
                print_error(f"[red]Could not upload error,[/] Raw Data: {reqjson or 'Could not get'}")
                url = "No URL"
            else:
                url = f"https://hastebin.com/{key}.txt"

            if HAS_RICH:
                # We make a traceback object for rich
                trace = Traceback.extract(type(error), error, error.__traceback__, show_locals=True)
                # We make a printable version of the traceback
                rich_tb = Traceback(trace=trace)
                # We print the traceback
                rich.print(rich_tb)

            # If the user is the owner then we send the info
            if await self.bot.is_owner(ctx.author):
                embed = discord.Embed(
                    title="Error",
                    description=f"HTML File Saved: `errors/error_{report.timestamp}.html`\n"
                    f"Text File Saved: `errors/error_{report.timestamp}.txt`\n"
                    f"Text File Cloud: {url}",
                )
                # We send the error and then delete it after 10 secs
                await ctx.send(embed=embed, delete_after=10)
            else:
                embed = discord.Embed(
                    title="Error Occured",
                    description=f"The Error code is `{report.timestamp}`. pls ask the owner to fix",
                )
                # We send the error and then delete it after 2 mins
                await ctx.send(embed=embed, delete_after=120)


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Errors(bot))

import ast
import io
import pprint
import textwrap
import traceback

import discord
from discord.ext import commands

import utils
from utils.converters import CodeblockConverter
from utils.functions import get_agreement
from utils.paginator import Paginator


def insert_returns(body):
    """Inserts return statements"""
    # insert return statement if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class Owner(commands.Cog):
    """Commands only available to be used by the bot owner"""

    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.group(invoke_without_command=False, aliases=["msg"], name="bot_message")
    async def _bot_message(self, ctx):
        """To do stuff with the bot's messages"""

    @_bot_message.command(name="delete", aliases=["d"])
    @commands.is_owner()
    async def message_delete(self, ctx, msg: discord.Message):
        """Deletes the specified message"""
        try:
            await msg.delete()
        except discord.DiscordException as e:
            await ctx.send(e)

    @_bot_message.command(name="edit", aliases=["e"])
    @commands.is_owner()
    async def message_edit(self, ctx, msg: discord.Message, content: str):
        """Edits the specified message with the specified content"""
        try:
            await msg.edit(content=content, embeds=msg.embeds)
        except discord.DiscordException as e:
            await ctx.send(e)

    @_bot_message.command(name="delete_embed", aliases=["de"])
    @commands.is_owner()
    async def message_delete_embed(self, ctx, msg: discord.Message):
        """Removes all embeds from the specified message"""
        try:
            await msg.edit(content="‌" + msg.content, embed=None)
        except discord.DiscordException as e:
            await ctx.send(e)

    @commands.command()
    @commands.is_owner()
    async def leaveserver(self, ctx):
        """This makes the bot leave the server"""
        if get_agreement(ctx, "Are you sure you want me to leave?"):
            ctx.guild.leave()
        else:
            await ctx.send("Okay 😁")

    @commands.command(aliases=["shutup"])
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shuts the bot down"""
        await self.bot.close()

    @commands.group(
        name="blockfromusingthebot",
        aliases=["bfutb", "bfb", "blockfrombot"],
    )
    async def blockfrombot(self, ctx, task: str):
        """Blocks the specified user from using the bot."""

    @blockfrombot.command(name="add", aliases=["a", "new"])
    async def blockfrombot_add(self, ctx, user: discord.User):
        """Adds a new user to the bot's blocked users."""
        await self.bot.db.execute(
            """
            INSERT INTO blocks (user_id)
            VALUES ($1);
            """,
            user.id,
        )
        await ctx.send("Done")

    @blockfrombot.command(name="remove", aliases=["r", "delete", "d"])
    async def blockfrombot_remove(self, ctx, user: discord.User):
        """Deletes the specified user from the bot's blocked users."""
        user = await self.bot.db.fetchrow(
            """
            DELETE FROM blocks
            WHERE user_id=$1
            RETURNING *;
            """,
            user.id,
        )
        if not user:
            return await ctx.send("He was not blocked")
        await ctx.send("Done")

    @blockfrombot.command(name="list", aliases=["all", "l"])
    async def blockfrombot_list(self, ctx):
        """Sends all the users in the bot's blocked users"""
        list_of_users = await self.bot.db.fetch(
            """
            SELECT *
            FROM blocks
            LIMIT 20;
            """
        )
        blocked_users = []
        for i in list_of_users:
            # idk why I do this but idk what to do about it
            user_id = list(i.values())[0]
            # We get the user
            user = self.bot.get_user(user_id)
            # We add the user name#discrim if it shares a server with the bot else we add the id
            blocked_users.append(str(user) if user else user_id)
        nl = "\n"
        await ctx.send(
            embed=discord.Embed(
                title="Blocked Users",
                description=f"```{nl.join(blocked_users)}```",
            )
        )

    @commands.command(aliases=["rein"])
    async def reinvoke(self, ctx, message: discord.Message = None):
        """Re-invokes the command gotten from the message

        You can also reply to the message to get the command from it
        """
        if message is None:
            if ctx.message.reference:
                message = ctx.message.reference.resolved
            else:
                return await ctx.send("No message was given :no_entry:")
        await self.bot.process_commands(message)

    @commands.command(aliases=["curl"])
    @commands.is_owner()
    async def get(self, ctx, url: str):
        """Returns the response from the specified website url"""
        # remove embed maskers if present
        url = url.lstrip("<").rstrip(">")

        async with self.bot.session.get(url) as response:
            data = await response.text()
            code = response.status

        if not data:
            return await ctx.send(f"HTTP response was empty (status code {code}).")

        if len(data) < 1023:
            embed = discord.Embed(title="Response", description="```json\n" + data + "\n```")
            await ctx.send(embed=embed)
        else:
            await ctx.send(file=discord.File(io.StringIO(data), filename="response.json"))

    @commands.command(name="eval", aliases=["e"])
    @commands.is_owner()
    async def eval_command(self, ctx, *, cmd: CodeblockConverter):
        """Evaluates input.
        Input is interpreted as newline seperated statements.
        If the last statement is an expression, that is the return value.
        Usable globals:
        - `bot`: the bot instance
        - `discord`: the discord module
        - `commands`: the discord.ext.commands module
        - `ctx`: the invokation context
        - `__import__`: the builtin `__import__` function
        Such that `>eval 1 + 1` gives `2` as the result.
        The following invokation will cause the bot to send the text '9'
        to the channel of invokation and return '3' as the result of evaluating
        >eval ```
        a = 1 + 2
        b = a * 2
        await ctx.send(a + b)
        a
        ```
        """
        fn_name = "_eval_expr"
        # add a layer of indentation
        cmd: str = textwrap.indent(cmd.content, "    ")

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            "bot": ctx.bot,
            "discord": discord,
            "commands": commands,
            "ctx": ctx,
            "guild": ctx.guild,
            "author": ctx.author,
            "channel": ctx.channel,
            "message": ctx.message,
            "client": ctx.bot,
            "__import__": __import__,
            "utils": utils,
        }
        # We add our current globals to the environment
        env.update(globals())
        # We add a yellow circle to specify that the code is being executed
        await ctx.message.add_reaction("\U0001f7e1")  # 🟡

        exec(compile(parsed, filename="<eval>", mode="exec"), env)
        result = await eval(f"{fn_name}()", env)
        # We add a green circle to indicate that the code was executed successfully and remove the yellow circle
        await ctx.message.add_reaction("\U0001f7e2")  # 🟢
        await ctx.message.remove_reaction("\U0001f7e1", ctx.me)  # 🟡

        # We format the result
        parsed_result = None
        if isinstance(result, str):
            parsed_result = result.replace(
                self.bot.http.token, "ODczNjA5Njg4NTczNDI3NzQy.YQ66bA.GeWX0EpfT1iYftF7cTJbeJTk1JU"
            )
        elif isinstance(result, (int, float, bool)):
            parsed_result = str(result)
        elif isinstance(result, (list, dict)):
            parsed_result = pprint.pformat(result)
        elif isinstance(result, discord.File):
            await ctx.send(file=result)
        elif isinstance(result, discord.Embed):
            await ctx.send(embed=result)
        elif result is None:
            parsed_result = "None"
        else:
            parsed_result = repr(result)

        # If the result is empty then we stop
        if not parsed_result:
            return

        # If the result is less than 2000 characters long then we just send it
        if len(parsed_result) < 2000:
            return await ctx.send(f"```python\n{parsed_result}```")

        # If the result is longer than 2000 characters then we send it with pagination
        pag = commands.Paginator(prefix="```python", suffix="```")

        for line in parsed_result.splitlines():
            pag.add_line(line)

        embeds = []
        for page in pag.pages:
            embeds.append(discord.Embed(title="Result", description=page))

        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @eval_command.error
    async def on_eval_error(self, ctx, error):
        """This handles errors"""
        # We add a red circle to indicate that the code execution failed and remove the yellow circle
        await ctx.message.remove_reaction("\U0001f7e1", ctx.me)
        await ctx.message.add_reaction("\U0001f534")

        trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        embed = discord.Embed(title="Error", description="Code Evaluation raised a error:")
        if len(trace) < 1023:
            embed.add_field(name="Traceback", value="```python\n" + trace + "\n```", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, file=discord.File(io.StringIO(trace), filename="traceback.py"))


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Owner(bot))

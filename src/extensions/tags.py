"""File for the tags cog"""
# FIXME: the db calls need to be fixed
import datetime

import discord
import humanize
from discord.ext import commands
from utils.functions import split_by_slice
from utils.paginator import Paginator


class Tags(commands.Cog):
    """Tag System"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_subcommands=True, aliases=["tg"], signature="<tag_name>")
    async def tag(self, ctx):
        """Shows the content of a tag"""
        if ctx.invoked_subcommand:
            return
        tag_name = ctx.message.content.replace(ctx.prefix + ctx.invoked_with, "").strip()
        # print(tag_name)
        tag = await self.bot.db.fetchrow(
            """
            SELECT * FROM tags WHERE NAME = $1
            """,
            tag_name,
        )
        if not tag:
            return await ctx.send("Tag doesn't exist")
        await self.bot.db.execute(
            """
            UPDATE tags
            SET last_used = $1
            WHERE name = $2
            """,
            datetime.datetime.utcnow(),
            tag_name,
        )
        await ctx.send(tag["content"])

    @tag.command(name="raw")
    async def tag_raw(self, ctx):
        """Shows the content of a tag"""
        if ctx.invoked_subcommand:
            return
        tag_name = ctx.message.content.replace(ctx.prefix + ctx.invoked_with, "").strip()
        # print(tag_name)
        tag = await self.bot.db.fetchrow(
            """
            SELECT * FROM tags WHERE NAME = $1
            """,
            tag_name,
        )
        if not tag:
            return await ctx.send("Tag doesn't exist")
        await self.bot.db.execute(
            """
            UPDATE tags
            SET last_used = $1
            WHERE name = $2
            """,
            datetime.datetime.utcnow(),
            tag_name,
        )
        await ctx.send(discord.utils.escape_markdown(tag["content"]))

    @tag.command(name="create", aliases=["add", "c", "a"])
    async def tag_create(self, ctx, tag_name, *, tag_content):
        """
        Creates a new tag

        For tag content to contain multiple words, use "", for example `wm,tag create example "example hi"`
        """
        tag = await self.bot.db.fetch(
            """
            SELECT * FROM tags WHERE NAME = $1
            """,
            tag_name,
        )
        if tag:
            return await ctx.send("Tag already exists")
        await self.bot.db.execute(
            """
            INSERT INTO tags (name, content, created_at, author_id)
            VALUES ($1, $2, $3, $4)
            """,
            tag_name,
            tag_content,
            datetime.datetime.utcnow(),
            ctx.author.id,
        )
        await ctx.send("Tag created")

    @tag.command(name="edit", aliases=["change", "e"])
    async def tag_edit(self, ctx, tag_name, *, tag_content):
        """Edits an existing tag

        For tag content to contain multiple words, use "", for example `wm,tag create example "example hi"`
        """
        tag = await self.bot.db.fetchrow(
            """
            SELECT * FROM tags WHERE NAME = $1
            """,
            tag_name,
        )
        if not tag:
            return await ctx.send("Tag doesn't exist")
        if tag["author_id"] != ctx.author.id:
            return await ctx.send("Tag not owned by you")
        await self.bot.db.execute(
            """
                    UPDATE tags
                    SET content = $2, edited_at = $3
                    WHERE name = $1;
                    """,
            tag_content,
            tag_name,
            datetime.datetime.utcnow(),
        )
        await ctx.send("Tag edited")

    @tag.command(name="info", aliases=["about", "author", "i"])
    async def tag_info(self, ctx, tag_name):
        """Shows Information about a tag"""

        tag = await self.bot.db.fetchrow(
            """
            SELECT * FROM tags WHERE NAME = $1
            """,
            tag_name,
        )
        if not tag:
            return await ctx.send("Tag doesn't exist")

        embed = discord.Embed(title=tag["name"])
        user = self.bot.get_user(tag["author_id"])
        embed.set_thumbnail(url=user.avatar.url if user else discord.Embed.Empty)
        embed.add_field(name="Author", value=f"{user} (ID: `{user.id})`", inline=False)
        embed.add_field(
            name="Created at",
            value=f'{tag["created_at"].strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.datetime.utcnow() - tag["created_at"])})',
            inline=False,
        )
        embed.add_field(
            name="Last used at",
            value=f'{tag["last_used"].strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.datetime.utcnow() - tag["last_used"])})',
            inline=False,
        )
        await ctx.send(embed=embed)

    @tag.command(name="delete", aliases=["remove", "r", "d"])
    async def tag_delete(self, ctx, tag_name):
        """
        Deletes a tag

        You must be the owner of the tag to delete it
        """
        tag = await self.bot.db.fetchrow(
            """
            SELECT * FROM tags WHERE NAME = $1
            """,
            tag_name,
        )
        if not tag:
            return await ctx.send("Tag doesn't exist")
        if tag["author_id"] != ctx.author.id:
            return await ctx.send("Tag not owned by you")
        await self.bot.db.execute(
            """
            DELETE FROM tags WHERE name = $1
            """,
            tag_name,
        )
        await ctx.send("Tag deleted succesfully")

    @tag.command(name="all", aliases=["every"])
    async def tag_all(self, ctx):
        """Shows all tags"""
        all_tags = await self.bot.db.fetch(
            """
            SELECT * FROM tags
            """
        )
        embeds = []
        for tag_page in split_by_slice(all_tags, 30):
            embed = discord.Embed(title="All Tags")
            description = ""
            for tag in tag_page:
                description += f"**{tag['tag_id']}**. {tag['name']}\n"
            embed.description = description
            embeds.append(embed)
        menu = Paginator(embeds)
        await menu.start(ctx)

    @commands.command(aliases=["every"])
    async def tags(self, ctx, member: discord):
        """Show all tags of a user"""
        all_tags = await self.bot.db.fetch(
            """
            SELECT * FROM tags WHERE author_id = $1
            """,
            member.id,
        )
        embeds = []
        for tag_page in split_by_slice(all_tags, 30):
            embed = discord.Embed(title=f"All Tags by {member.name}")
            description = ""
            for tag in tag_page:
                description += f"**{tag['tag_id']}**. {tag['name']}\n"
            embed.description = description
            embeds.append(embed)
        menu = Paginator(embeds)
        await menu.start(ctx)


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Tags(bot))

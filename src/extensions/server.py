import difflib
import json
from collections import Counter

import discord
from discord.ext import commands
from discord.ext.commands import BucketType

from utils.functions import format_name, split_by_slice
from utils.paginator import Paginator


class Server(commands.Cog):
    """Server releated commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["setprefix", "setwmbotprefix"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def prefix(self, ctx, prefix: str):
        """Changes the prefix for a server"""
        await self.bot.db.execute(
            """
            UPDATE guilds
            SET prefix = $2
            WHERE id = $1;
            """,
            ctx.guild.id,
            prefix,
        )
        await ctx.send(f"prefix set to `{prefix}`")

    @commands.command(aliases=["guildinfo", "si", "gi"])
    async def serverinfo(self, ctx):
        """See the information of the current server"""
        guild = ctx.guild
        guild_owner = self.bot.get_user(guild.owner_id)

        features = "\n".join(format_name(f) for f in guild.features)

        embed = discord.Embed(
            title=f"Server Information for {guild.name}",
            description=(
                f"Name: {guild.name}\n"
                f"Created At: {discord.utils.format_dt(guild.created_at, 'F')} ({discord.utils.format_dt(guild.created_at, 'R')})"
                f"ID: {guild.id}\nOwner: {guild_owner}\n"
                f"Icon Url: [click here]({guild.icon.url if guild.icon else None})\n"
                f"Verification Level: {str(guild.verification_level)}\n"
                f"Members: {len(guild.members)}\n"
                f"{self.bot.get_custom_emoji('server.boost_level')} Boost Level: {guild.premium_tier}\n"
                f"{self.bot.get_custom_emoji('server.boosts')} Boosts: {guild.premium_subscription_count}\n"
                f"{self.bot.get_custom_emoji('server.boosters')} Boosters: {len(guild.premium_subscribers)}\n"
                f"Total Channels: {len(guild.channels)}\n"
                f"{self.bot.get_custom_emoji('server.text_channel')} Text Channels: {len(guild.text_channels)}\n"
                f"{self.bot.get_custom_emoji('server.voice_channel')} Voice Channels: {len(guild.voice_channels)}\n"
                f"{self.bot.get_custom_emoji('server.category_channel')} Categories: {len(guild.categories)}\n"
                f"Roles: {len(guild.roles)}\n"
                f"Emojis: {len(guild.emojis)}/{guild.emoji_limit}\n"
                f"Upload Limit: {round(guild.filesize_limit / 1048576)} Megabytes (MB)\n"
                f"**Features:** {features}"
            ),
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        await ctx.send(embed=embed)

    @commands.command()
    async def boosters(self, ctx):
        """Sends all the boosters of this server"""
        people_who_boosted = sorted(ctx.guild.premium_subscribers, key=lambda member: member.joined_at)

        if not people_who_boosted:
            return await ctx.send("No one has boosted this server yet")

        peoples = commands.Paginator(max_size=500, prefix="```ini\n", suffix="```")
        for n, i in enumerate(people_who_boosted):
            peoples.add_line(f"[{n}] {i.name} ID: [{i.id}]")

        embeds = []
        for page in peoples.pages:
            embeds.append(discord.Embed(title=f"{len(people_who_boosted)} Boosters", description=page))

        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @commands.command(
        aliases=["memlist", "allmembers", "am", "servermembers", "sm", "memberslist"],
    )
    async def memberlist(self, ctx):
        """See all the members of this server sorted by their top role"""
        people = sorted(ctx.guild.members, key=lambda member: member.top_role, reverse=True)

        peoples = commands.Paginator(max_size=500, prefix="```ini\n", suffix="```")
        for num, i in enumerate(people, 1):
            peoples.add_line(f"[{num}] {i.name}\n    [ID] {i.id} [TOP ROLE] {i.top_role.name}")

        embeds = []
        for page in peoples.pages:
            embeds.append(discord.Embed(title=f"{len(people)} Members", description=page))

        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @commands.command(
        aliases=["fj", "whojoinedfirst", "wjf", "firstmembers", "fmem", "oldmembers"],
    )
    async def firstjoins(self, ctx):
        """See all the members of this server sorted by their join time"""
        embeds = []
        people = sorted(ctx.guild.members, key=lambda member: member.joined_at)

        for chunk in split_by_slice(people, 5):
            embed = discord.Embed()
            for people in chunk:
                embed.add_field(
                    name=f"{people.name} (ID: {people.id})",
                    value=f'Created at: {discord.utils.format_dt(people.created_at, "F")} ({discord.utils.format_dt(people.created_at, "R")})\n'
                    f'Joined at: {discord.utils.format_dt(people.joined_at, "F")} ({discord.utils.format_dt(people.joined_at, "R")})',
                    inline=False,
                )
            embeds.append(embed)

        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @commands.command(
        aliases=["nj", "whojoinedlast", "wjl", "lastmembers", "lm", "newmembers"],
    )
    async def newjoins(self, ctx):
        """See the newest members of this server"""
        people = sorted(ctx.guild.members, key=lambda member: member.joined_at, reverse=True)

        embeds = []
        for chunk in split_by_slice(people, 5):
            embed = discord.Embed(title=f"{len(people)} Members")
            for people in chunk:
                embed.add_field(
                    name=f"{people.name} (ID: {people.id})",
                    value=f'Created at: {discord.utils.format_dt(people.created_at, "F")} ({discord.utils.format_dt(people.created_at, "R")})\n'
                    f'Joined at: {discord.utils.format_dt(people.joined_at, "F")} ({discord.utils.format_dt(people.joined_at, "R")})',
                )
            embeds.append(embed)

        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @commands.command()
    async def bots(self, ctx):
        """See all the bots in this server sorted by their join date"""
        people = filter(lambda member: member.bot, ctx.guild.members)
        people = sorted(people, key=lambda member: member.joined_at)

        peoples = commands.Paginator(max_size=500, prefix="```ini\n", suffix="```")
        for n, i in enumerate(people, 1):
            peoples.add_line(f"[{n}] {i.name} [ID] {i.id}")

        embeds = []
        for page in peoples.pages:
            embeds.append(discord.Embed(title=f"{len(people)} Bots", description=page))

        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @commands.command()
    async def humans(self, ctx):
        """Sends all the humans of this server sorted by their join date"""
        people = filter(lambda member: not member.bot, ctx.guild.members)
        people = sorted(people, key=lambda member: member.joined_at)

        peoples = commands.Paginator(max_size=500, prefix="```ini\n", suffix="```")
        for n, i in enumerate(people, 1):
            peoples.add_line(f"[{n}] {i.name} [ID: {i.id}]")

        embeds = []
        for page in peoples.pages:
            embeds.append(discord.Embed(title=f"{len(people)} Humans", description=page))

        paginator = Paginator(embeds)
        await paginator.start(ctx)

    async def get_emoji_from_api(self, ctx, emoji_name: str):
        if not hasattr(ctx.bot, "emoji_list") or len(ctx.bot.emoji_list) == 0:
            msg1 = await ctx.send(f"Loading emojis {self.bot.get_custom_emoji('load.typing')}")

            async with self.bot.session.get("https://emoji.gg/api") as resp:
                ctx.bot.emoji_list = json.loads(await resp.text())
            await msg1.delete()
            ctx.bot.emoji_list_str = [i["title"].lower() for i in ctx.bot.emoji_list]

        emoji_from_api = next((i for i in ctx.bot.emoji_list if i["title"].lower() == emoji_name.lower()), None)
        
        if emoji_from_api is None:
            embed = discord.Embed(
                title="Emoji not found",
                description=f"Did you mean any of these?\n{', '.join(difflib.get_close_matches(emoji_name.lower(), ctx.bot.emoji_list_str, n=5, cutoff=0.2))}",
                color=0x2F3136,
            )
            await ctx.send(embed=embed)
            return None
        return emoji_from_api

    @commands.group(description="Adds or views a emoji from https://emoji.gg to your server", invoke_without_command=True)
    async def emoji(self, ctx):
        await ctx.send_help(ctx.command)

    @emoji.command(name="view")
    async def emoji_view(self, ctx, emoji_name: str):
        emoji_from_api = await self.get_emoji_from_api(ctx, emoji_name)
        if not emoji_from_api:
            return
            
        embed = discord.Embed(
            title=emoji_name,
            url=emoji_from_api["image"].replace("discordemoji.com", "emoji.gg"),
            color=0x2F3136,
        )
        embed.add_field(name="Author", value=emoji_from_api["submitted_by"])
        embed.set_thumbnail(url=emoji_from_api["image"].replace("discordemoji.com", "emoji.gg"))
        embed.set_image(url=emoji_from_api["image"].replace("discordemoji.com", "emoji.gg"))
        embed.set_footer(
            text="Because of a discord bug, we may bot be able to show the emoji as a big image, so here is the small version",
            icon_url=emoji_from_api["image"],
        )
        await ctx.send(embed=embed)

    @emoji.command(name="add")
    @commands.has_permissions(manage_emojis=True)
    async def emoji_add(self, ctx, emoji_name: str):
        emoji_from_api = await self.get_emoji_from_api(ctx, emoji_name)
        if not emoji_from_api:
            return
            
        async with self.bot.session.get(emoji_from_api["image"]) as r:
            try:
                emoji = await ctx.guild.create_custom_emoji(name=emoji_name, image=await r.read())
                await ctx.send(f"Emoji {emoji} added succesfully :)")
            except discord.Forbidden:
                await ctx.send("Unable to add emoji, check my permissions and try again")

    @commands.command(aliases=["flags"])
    @commands.cooldown(1, 60, BucketType.user)
    async def badges(self, ctx, server: discord.Guild = None):
        """Shows the amount of badges in the server. Kind of a useless command."""
        count = Counter()
        guild = server or ctx.guild

        for member in guild.members:
            for flag in member.public_flags.all():
                count[flag.name] += 1

        msg = ""
        count = dict(reversed(sorted(count.items(), key=lambda item: item[1])))
        for k, v in count.items():
            msg += f"{format_name(k)}: **{v}**\n\n"

        embed = discord.Embed()
        embed.set_author(name=f"Badge Count in {guild.name}", icon_url=guild.icon.url if guild.icon else None)
        await ctx.send(embed=embed)


async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(Server(bot))

import re
from typing import Optional, Union

import discord
from discord.ext import commands

from utils.converters import TimeConverter
from utils.functions import find_user_named, format_name, get_agreement
from utils.paginator import Paginator


class Moderation(commands.Cog):
    """commands to help you moderate a server"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks a member from the server."""

        if ctx.author.top_role <= member.top_role:
            return await ctx.send(
                f"Your top role is lower than or equal to {member}'s top role therefore you cannot kick them"
            )

        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member.mention}")

    @commands.command(
        aliases=["setnick", "setnickname", "nickname", "changenickname", "chnick"],
    )
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, nick):
        """Changes the nickname of a person"""
        await member.edit(nick=nick)
        await ctx.send(f"Nickname was changed for {member.mention} ")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bans a member from the server."""
        if ctx.author.top_role <= member.top_role:
            return await ctx.send(
                f"Your top role is lower than or equal to {member}'s top role therefore you cannot ban them"
            )

        await member.ban(reason=reason)
        await ctx.send(f"Banned {member.mention}")

    @commands.command(aliases=["rb"])
    @commands.has_permissions(view_audit_log=True)
    async def recentbans(self, ctx):
        """Shows the recent bans, who banned them and why"""
        embeds = []

        async for entry in ctx.guild.audit_logs(action=discord.AuditLogAction.ban):
            embed = discord.Embed(title="Bans", timestamp=entry.created_at, color=0x2F3136)
            embed.add_field(
                name="Banned user",
                value=f"{entry.target} (ID: {entry.target.id})",
                inline=False,
            )
            embed.add_field(name="Author", value=f"{entry.user} (ID: {entry.user.id})", inline=False)
            embed.add_field(name="Reason", value=f"{entry.reason}", inline=False)

            embeds.append(embed)

        menu = Paginator(embeds)
        await menu.start(ctx)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user: Union[int, str]):
        """Bans a user by their name#discriminator or their name or their id"""
        if isinstance(user, str):
            banned_users = await ctx.guild.bans()
            user = find_user_named(banned_users, user)
            if user:
                await ctx.guild.unban(user)
                await ctx.send(f"Unbanned {user.mention}")
            else:
                await ctx.send("User not found, maybe try using their id")
        else:
            await ctx.guild.unban(discord.Object(id=user))
            await ctx.send("Unbanned the user")

    @commands.group(aliases=["clear", "purge", "c"])
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    @commands.has_permissions(manage_messages=True)
    async def prune(self, ctx, amount: int):
        """ Removes messages from the current server. """
        if ctx.invoked_subcommand:
            return
        messages = await ctx.channel.purge(limit=amount)
        deleted = len(messages)
        await ctx.send(f"🚮 Successfully removed {deleted} message{'' if deleted == 1 else 's'}.")

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None, message=True):
        if limit > 2000:
            return await ctx.send(f"Too many messages to search given ({limit}/2000)")

        if not before:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden:
            return await ctx.send("I do not have permissions to delete messages.")
        except discord.HTTPException as e:
            return await ctx.send(f"Error: {e} (try a smaller search?)")

        deleted = len(deleted)
        if message is True:
            await ctx.send(f"🚮 Successfully removed {deleted} message{'' if deleted == 1 else 's'}.")

    @prune.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @prune.command()
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @prune.command()
    async def mentions(self, ctx, search=100):
        """Removes messages that have mentions in them."""
        await self.do_removal(ctx, search, lambda e: len(e.mentions) or len(e.role_mentions))

    @prune.command()
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @prune.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @prune.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send("The substring length must be at least 3 characters.")
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @prune.command(name="bots")
    async def _bots(self, ctx, search=100, prefix=None):
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return m.webhook_id is None and m.author.bot

        await self.do_removal(ctx, search, predicate)

    @prune.command(name="users")
    async def _users(self, ctx, search=100):
        """Removes only user messages. """

        def predicate(m):
            return m.author.bot is False

        await self.do_removal(ctx, search, predicate)

    @prune.command(name="emojis")
    async def _emojis(self, ctx, search=100):
        """Removes all messages containing emojis."""
        custom_emoji = re.compile(r"<a?:(.*?):(\d{17,21})>|[\u263a-\U0001f645]")

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @prune.command(name="reactions")
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(f"Too many messages to search for ({search}/2000)")

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f"Successfully removed {total_reactions} reactions.")

    @commands.command()
    async def mute(self, ctx, user: discord.Member, reason=None):
        """Mutes a user with a optional reason

        If the guild has a muted role then it uses that role and if not, creates a muted role
        """
        role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not role:
            # First we create a Muted role
            try:
                muted = await ctx.guild.create_role(name="Muted", reason="To use for muting")
            except discord.Forbidden:
                return await ctx.send(
                    "The server does not have a Muted role and I have no permissions "
                    "to make a muted role. create a Muted role yourself or give me permissions "
                    "to create a Muted role"
                )
            # We edit the permissions for every channel in the server
            failed = []
            done = []
            for channel in ctx.guild.channels:
                try:
                    await channel.set_permissions(
                        muted,
                        send_messages=False,
                        read_messages=False,
                    )
                except discord.Forbidden:
                    failed.append(channel)
                else:
                    done.append(channel)
            # If we couldn't set permissions for any channel at all,
            # we delete the role and send a message
            if not done:
                await muted.delete()
                return await ctx.send(
                    "I do not have permissions to edit channels to make the muted role work "
                    "Give me the proper permissions or make a muted role yourself add edit each channel "
                    "in this server and disable permissions for the muted role"
                )
            # If we couldn't set permissions for a few channels, we send a message'
            if failed:
                return await ctx.send(
                    f"Changed permissions for {len(done)} channels, Could not change permissions "
                    f"for the following channels: {', '.join(i.name for i in failed)}\n"
                    f"Change the permissions for those channels yourself or else the mute won't work"
                )

        if role in user.roles:
            return await ctx.send(f"{user} is already muted")

        await user.add_roles(role)
        await ctx.send(f"{user.mention} has been muted for {reason}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, user: discord.Member):
        """Unmutes a muted member"""
        try:
            await user.remove_roles(discord.utils.get(ctx.guild.roles, name="Muted"))
            await ctx.send(f"{user.mention} has been unmuted")
        except discord.Forbidden:
            await ctx.send("No Permissions")

    @commands.command(aliases=["sd"])
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, channel: Optional[discord.TextChannel] = None, slowmode: TimeConverter = None):
        """Change the current slowmode of the channel,

        The slowmode and channel are optional, slowmode defaults to 5 and channel defaults to the current channel
        """
        slowmode = slowmode or 5
        channel = channel or ctx.channel

        if slowmode > 21600:
            await ctx.send("Slow Mode too long")
        else:
            await channel.edit(slowmode_delay=slowmode)
            await ctx.send(f"Slow Mode set to {slowmode} seconds for {channel.mention}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member, *, role: discord.Role):
        """Changes roles for a member

        Removes if he has the role, adds the role if not"""
        if role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(colour=discord.Color.blue())
            embed.set_author(name=f"Role Changed for {member}")
            embed.set_footer(text=f"Done by {ctx.author}")
            embed.add_field(name="Removed Role", value=f"{role.mention}")
            await ctx.send(embed=embed)
        else:
            await member.add_roles(role)
            embed = discord.Embed(colour=discord.Color.green())
            embed.set_author(name=f"Role Changed for {member}")
            embed.set_footer(text=f"Done by {ctx.author}")
            embed.add_field(name="Added Role", value=f"{role.mention}")
            await ctx.send(embed=embed)

    @commands.command(aliases=["permissions"])
    async def perms(self, ctx, member: discord.Member = None, channel: discord.TextChannel = None):
        """See someone's permissions"""
        channel = channel or ctx.channel
        member = member or ctx.author

        permstr = ""
        for perm_name, value in dict(member.permissions_in(channel)):
            emoji = (
                self.bot.get_custom_emoji("validation.green_tick")
                if value
                else self.bot.get_custom_emoji("validation.red_tick")
            )
            permstr += f"{emoji} {format_name(perm_name)}\n"

        embed = discord.Embed(title=f"{member}'s Permissions", description=permstr, color=0x2F3136)
        await ctx.send(embed=embed)

    @commands.command(aliases=["nk"])
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx, channel: discord.TextChannel = None):
        """Nukes a channel

        Creates a new channel with all the same properties (permissions, name, topic etc.)
        and deletes the original one"""
        channel = channel or ctx.channel

        if await get_agreement(ctx, "Do you really want to nuke the channel?"):
            position = channel.position
            await channel.delete()

            newchannel = await channel.clone(reason=f"Nuked by {ctx.author}")
            newchannel.edit(position=position)

            await ctx.send("Channel Nuked")

    @commands.command(aliases=["cln"])
    @commands.has_permissions(manage_channels=True)
    async def clone(self, ctx, channel: discord.TextChannel = None):
        """Clones a channel

        Creates a duplicate channel with all the same properties (permissions, name, topic etc.)"""
        channel = channel or ctx.channel

        if await get_agreement(ctx, "Do you really want to clone the channel?"):
            await channel.clone(reason=f"Cloned by {ctx.author}")
            await ctx.send("Channel Cloned")

    @commands.command(aliases=["lck", "lk"])
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, *, role: discord.Role = None):
        """Locks a channel,

        it denys permission to send messages in a channel for everyone or the role specified"""
        role = role or ctx.guild.default_role
        channel = ctx.channel

        try:
            await channel.set_permissions(role, send_messages=False, read_messages=True)
            await ctx.send("Channel Locked")
        except discord.Forbidden:
            return await ctx.send("I do not have enough permissions to lock")

    @commands.command(aliases=["unlck", "ulk"])
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, *, role: discord.Role = None):
        """Unocks a channel,

        it allows permission to send messages in a channel for everyone or the role specified"""
        role = role or ctx.guild.default_role
        channel = ctx.channel

        try:
            await channel.set_permissions(role, send_messages=True, read_messages=True)
            await ctx.send("Channel Unlocked")
        except discord.Forbidden:
            return await ctx.send("I have no permissions to lock")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def block(self, ctx, user: discord.Member):
        """Blocks a user from chatting in current channel."""
        if ctx.author.top_role <= user.top_role:
            return await ctx.send(
                f"Your top role is lower than or equal to {user}'s top role therefore you cannot block them'"
            )
        try:
            await ctx.set_permissions(user, send_messages=False)
        except discord.Forbidden:
            await ctx.send("No permissions")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unblock(self, ctx, user: discord.Member):
        """Unblocks a previously blocked user from the channel"""
        if ctx.author.top_role <= user.top_role:
            return await ctx.send(
                f"Your top role is lower than or equal to {user}'s top role therefore you cannot unblock them'"
            )
        try:
            await ctx.set_permissions(user, send_messages=True)
        except discord.Forbidden:
            await ctx.send("No permissions")


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Moderation(bot))

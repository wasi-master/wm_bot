import datetime

import discord
import humanize
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class Information(commands.Cog):
    """Information commands releated to discord"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ii"])
    @commands.cooldown(1, 5, BucketType.user)
    async def inviteinfo(self, ctx, invite: commands.InviteConverter):
        """Get information about an invite"""

        embed = discord.Embed(
            title=invite.url,
            url=invite.url,
            color=discord.Color.red() if invite.revoked else discord.Color.blue(),
        )
        embed.description = (
            f"**Max Age**: {invite.max_age if invite.max_age else 'Unlimited'}\n"
            f"**Max Uses**: {invite.max_uses if invite.max_uses else 'Unlimited'}"
        )

        if ctx.guild and self.bot.get_user_named(f"{invite.inviter}#{invite.inviter.discriminator}"):
            embed.set_author(
                name=f"{invite.inviter}#{invite.inviter.discriminator}",
                icon_url=invite.inviter.avatar_url,
            )

        embed.add_field(name="For Channel", value=invite.channel if invite.channel else "No Channel", inline=False)
        embed.add_field(name="For Server", value=invite.guild, inline=False)
        embed.add_field(name="Inviter", value=invite.inviter, inline=True)

        if invite.created_at:
            embed.add_field(
                name="Created at",
                value=f'{discord.utils.format_dt(invite.created_at, "F")}  ({discord.utils.format_dt(invite.created_at, "R")})',
                inline=False,
            )
        if invite.expires_at:
            embed.add_field(
                name="Expires at",
                value=f'{discord.utils.format_dt(invite.expires_at, "F")}  ({discord.utils.format_dt(invite.expires_at, "R")})',
                inline=False,
            )
        else:
            embed.add_field(name="Expires at", value="Never")

        embed.add_field(
            name="Server Member count",
            value=invite.approximate_member_count,
            inline=True,
        )
        embed.add_field(
            name="Server Member online",
            value=invite.approximate_presence_count,
            inline=True,
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["ci", "chi"])
    async def channelinfo(self, ctx, channel: discord.abc.GuildChannel = None):
        """See information about a specific channel."""
        channel = channel or ctx.channel

        embed = discord.Embed(color=0x2F3136)

        embed.set_author(name=f"Channel Information for {channel.name}")
        if channel.topic:
            embed.add_field(name="Topic", value=channel.topic, inline=False)
        embed.add_field(
            name="Created at",
            value=f'{discord.utils.format_dt(channel.created_at, "F")}  ({discord.utils.format_dt(channel.created_at, "R")})',
        )
        embed.add_field(name="ID", value=channel.id)
        embed.add_field(name="Position", value=f"{channel.position}/{len(ctx.guild.text_channels)}")
        embed.add_field(name="Category", value=channel.category.name)
        if channel.slowmode_delay:
            embed.add_field(
                name="Slowmode",
                value=f"{channel.slowmode_delay} seconds ({humanize.naturaldelta(datetime.timedelta(seconds=int(channel.slowmode_delay)))})",
            )

        await ctx.send(embed=embed)

    @commands.command(aliases=["ri", "rlinf"])
    async def roleinfo(self, ctx, role: discord.Role):
        """See information about a role"""
        embed = discord.Embed(title=f"Role Information for {role.name}", colour=role.colour.value or 0x2F3136)

        embed.add_field(name="ID", value=role.id)
        embed.add_field(name="Members", value=len(role.members))
        embed.add_field(
            name="Position",
            value=f"{len(ctx.guild.roles) - role.position}/{len(ctx.guild.roles)}",
        )
        embed.add_field(
            name="Created at",
            value=f"{discord.utils.format_dt(role.created_at, 'F')} ({discord.utils.format_dt(role.created_at, 'R')})",
        )
        embed.add_field(
            name="Role Color",
            value=f"INT: {role.color.value}\nHEX: {hex(role.colour.value)[2:].zfill(6)}\nRGB: rgb{role.color.to_rgb()}",
        )
        embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No")
        embed.add_field(name="Displayed Separately?", value="Yes" if role.hoist else "No")

        await ctx.send(embed=embed)

    @commands.command(aliases=["ei", "emoteinfo"])
    async def emojiinfo(self, ctx, emoji: discord.Emoji):
        """Shows info about a emoji"""
        embed = discord.Embed(title=emoji.name, description="\\" + str(emoji))
        embed.set_thumbnail(url=emoji.url)
        embed.set_image(url=emoji.url)
        embed.add_field(name="ID", value=emoji.id)
        if emoji.user:
            embed.add_field(name="Added by", value=emoji.user)
        embed.add_field(name="Server", value=emoji.guild)
        embed.add_field(
            name="Created at",
            value=f'{discord.utils.format_dt(emoji.created_at, "F")} ({discord.utils.format_dt(emoji.created_at, "R")})',
        )
        embed.add_field(name="URL", value=f"[Click Here]({emoji.url})")
        await ctx.send(embed=embed)


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Information(bot))

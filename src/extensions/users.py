import datetime
from io import BytesIO

import discord
import humanize
from discord.ext import commands
from utils.functions import (
    convert_sec_to_min,
    get_flag,
    get_p,
    get_status,
)


class Users(commands.Cog):
    """Details About Users"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=["nafk", "unafk", "rafk", "removeafk", "dafk", "disableafk"]
    )
    async def notawayfromkeyboard(self, ctx):
        """Removes your afk status"""
        is_afk = await self.bot.db.fetchrow(
            """
            DELETE FROM afk
            WHERE user_id=$1
            RETURNING *
            """,
            ctx.author.id,
        )
        if not is_afk:
            return await ctx.send("You are not afk")
        await ctx.send("Removed your afk status")

    @commands.command(aliases=["afk"])
    async def awayfromkeyboard(self, ctx, *, reason: commands.clean_content = None):
        """Sets your afk status"""
        # FIXME: use a single query instead
        is_afk = await self.bot.db.fetchrow(
            """
                SELECT *
                FROM afk
                WHERE user_id=$1
                """,
            ctx.author.id,
        )
        time = datetime.datetime.utcnow()
        if is_afk is None:
            await self.bot.db.execute(
                """
                    INSERT INTO afk (last_seen, user_id, reason)
                    VALUES ($1, $2, $3)
                    """,
                time,
                ctx.author.id,
                reason,
            )
        else:
            await self.bot.db.execute(
                """
                UPDATE afk
                SET last_seen = $1,
                reason = $2
                WHERE user_id = $3;
                """,
                time,
                reason,
                ctx.author.id,
            )
        if reason:
            await ctx.send(f"You are now afk for {reason} :)")
        else:
            await ctx.send("You are now afk :)")

    @commands.command(
        aliases=["pfp", "av", "profilepicture", "profile"],
    )
    async def avatar(self, ctx, *, user: discord.User = None):
        """See someone's avatar, if user is not provided then it shows your avatar"""
        user = user or ctx.author
        ext = "gif" if user.is_avatar_animated() else "png"

        await ctx.send(
            file=discord.File(BytesIO(await user.avatar.url.read()), f"{user}.{ext}")
        )

    @commands.command(
        aliases=["ui", "whois", "wi", "whoami", "me"],
    )
    async def userinfo(self, ctx, *, member: discord.Member = None):
        """Shows info about a user"""
        member = member or ctx.author

        status = await self.bot.db.fetchrow(
            """
            SELECT *
            FROM status
            WHERE user_id=$1
            """,
            member.id,
        )

        # Badges
        flags = list(member.public_flags.all())

        join_position = (
            sorted(ctx.guild.members, key=lambda member: member.joined_at).index(member)
            + 1
        )
        embed = discord.Embed(colour=member.color)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_author(name=f"{member}", icon_url=member.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}")
        # If the mentioned user is the bot owner then we say that
        if member.id in self.bot.owner_ids:
            embed.add_field(
                name="Fun Fact:",
                value="He is the bot owner",
            )
        embed.add_field(name="ID: ", value=member.id)
        # if the member's real name and nickname are different, then we show their nickname too
        if member.nick:
            embed.add_field(name="Nickname:", value=member.display_name)
        # If the member is a bot then we show their position in all members and also in bots only
        if member.bot:
            bots = list(member for member in ctx.guild.members if member.bot)
            join_position_for_bots = sorted(bots, key=lambda member: member.joined_at).index(member) + 1
            embed.add_field(
                name="Join Position",
                value=f"{join_position:,}/{len(ctx.guild.members):,} "
                f"({join_position_for_bots:,}/{len(bots):,} in bots)"
            )
        else:
            embed.add_field(
                name="Join Position",
                value=f"{join_position:,}/{len(ctx.guild.members):,}"
            )

        # If the member has badges then we show them
        if len(flags) != 0:
            embed.add_field(name="Badges", value=" ".join(get_flag(flag) for flag in flags), inline=False)
        # if the member has their last seen time stored in the database then we display it
        if status is None and str(member.status) != "offline":
            try:
                embed.add_field(
                    name="Last Seen",
                    value=humanize.precisedelta(
                        datetime.datetime.utcnow() - status["last_seen"]
                    )
                    + " ago",
                )
            except TypeError:
                pass

        tempuser = await self.bot.fetch_user(member.id)
        embed.set_image(url=tempuser.banner.url)
        # get_status is a custom method that returns a emoji based on the status
        embed.add_field(
            name="Online Status",
            value=(
                f"{get_status(member.desktop_status.name)} Desktop\n"
                f"{get_status(member.web_status.name)} Web\n"
                f"{get_status(member.mobile_status.name)} Mobile"
            )
        )
        # We use the discord timestamp formatting to show dates and time
        embed.add_field(
            name="Created at",
            value=f'{discord.utils.format_dt(member.created_at, "F")} ({discord.utils.format_dt(member.created_at, "R")})',
            inline=False,
        )
        embed.add_field(
            name="Joined at:",
            value=f'{discord.utils.format_dt(member.joined_at, "F")} ({discord.utils.format_dt(member.joined_at, "R")})',
            inline=False,
        )

        # If the member has only one role it will be the @everyone one which we don't want to show
        if len(member.roles) != 1:
            embed.add_field(
                name=f"Roles ({len(member.roles)})",
                value=" | ".join([role.mention for role in list(reversed(member.roles))[:-1]]),
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.command(
        aliases=["spt"]
    )
    async def spotify(self, ctx, *, member: discord.Member = None):
        """See your or another users spotify info"""
        member = member or ctx.author

        for activity in member.activities:
            if not isinstance(activity, discord.Spotify):
                continue

            embed = discord.Embed(color=activity.color)
            embed.set_thumbnail(
                # Spotify Flat Logo Icon by Alexis Doreau taken from https://iconscout.com/icon/spotify-11 :)
                url="https://i.imgur.com/QFdr6IG.png"
            )
            embed.set_image(url=activity.album_cover_url)
            embed.add_field(name="Song Name", value=activity.title)

            if len(activity.artists) == 0:
                embed.add_field(name="Artist", value=activity.artist)
            else:
                embed.add_field(name="Artists", value=activity.artist)

            if hasattr(activity, "album"):
                embed.add_field(name="Album", value=activity.album)
            else:
                embed.add_field(name="Album", value="None")

            if len(str(activity.duration)[2:-7]) > 1:
                embed.add_field(
                    name="Song Duration", value=str(activity.duration)[2:-7]
                )

            embed.add_field(
                name="Spotify Link",
                value=f"[Click Here](https://open.spotify.com/track/{activity.track_id})",
            )
            # I don't know why I have this in a try except but I don't wanna remove it
            try:
                current_time = convert_sec_to_min(
                    (datetime.datetime.utcnow()- activity.start.replace(tzinfo=None)).total_seconds()
                )
                progress_bar = get_p(
                    (abs((datetime.datetime.utcnow()- activity.start.replace(tzinfo=None)).total_seconds())) /
                    (abs(((activity.start - activity.end)).total_seconds()) / 100),
                    length=13
                )
                total_time = str(activity.duration)[2:-7]
                embed.add_field(
                    name="Time", value=f"{current_time} {progress_bar} {total_time}", inline=False
                )
            except IndexError:
                pass
            embed.set_footer(text="Track ID: " + activity.track_id)
            await ctx.send(embed=embed)
            # We break the loop here because we already sent the message
            break
        else:
            await ctx.send("Not listening to spotify :(")


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Users(bot))

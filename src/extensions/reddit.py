import random
from datetime import datetime

import discord
from discord.ext import commands


class Reddit(commands.Cog):
    """Needs to be worked upon"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="subreddit", aliases=["sr"])
    async def _subreddit(self, ctx, subreddit, post_filter=None):
        """Gets a random post from a subreddit

        you can pass a optional post_filter that is either hot or top.
        so a command with hot as the post_filter would look like
        `subreddit r/memes hot`

        """
        # We format the subreddit name
        if not "r/" in subreddit:
            subreddit = "r/" + subreddit
        if len(subreddit.lstrip("r/")) > 21:
            return await ctx.send("Invalid subreddit")


        base = "https://www.reddit.com/"
        # We generate the url
        if post_filter is None:
            url = f"{base}{subreddit}.json"
        elif post_filter in ("hot", "top"):
            url = f"{base}{subreddit}/{post_filter}.json"
        else:
            return await ctx.send("Invalid post filter")

        async with self.bot.session.get(url, allow_redirects=True) as resp:
            response = await resp.json()

        # The reason key is only present in errors
        if response.get("reason"):
            return await ctx.send(response["reason"])

        data = response["data"]["children"]
        # If this not a nsfw channel then we only pick posts that are not marked nsfw
        if ctx.guild and not ctx.channel.is_nsfw():
            data = [i for i in data if not i["data"]["over_18"]]
        # We pick a random post
        post = random.choice(data)["data"]

        embed = discord.Embed(
            title=post["title"],
            description=post["selftext"],
            timestamp=datetime.utcfromtimestamp(post["created"]),
            url=base + post["permalink"],
            color=0xFF5700,
        )
        if (url := post.get("url_overridden_by_dest")) is not None:
            embed.set_image(url=url)
        embed.set_author(
            name=f'Uploaded by u/{post["author"]}',
            url=f"https://www.reddit.com/u/{post['author']}",
        )

        await ctx.send(base + post["permalink"], embed=embed)


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Reddit(bot))

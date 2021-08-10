import io
import typing

import asyncdagpi
import discord
from discord.ext import commands
from utils.functions import executor_function, get_image, get_random_color


class Image(commands.Cog):

    """Image manipulation commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["qr"], extras={"image": ""})
    async def qrcode(self, ctx, text):
        """Converts the given text to a [qr code](https://en.wikipedia.org/wiki/QR_code)"""
        async with self.bot.session.get("https://api.qrserver.com/v1/create-qr-code", params={'size':'150x150', 'data':text}) as r:
            resp = await r.read()
            await ctx.send(
                embed=discord.Embed(color=get_random_color(), title="QR Code", description=text).set_image(
                    url="attachment://qr.png"
                ),
                file=discord.File(io.BytesIO(resp), filename="qr.png"),
            )

    @executor_function
    def rounden(self, img, ellipse: tuple):
        from PIL import Image, ImageDraw, ImageOps

        size = (1024, 1024)
        mask = Image.new("L", size, 255)
        draw = ImageDraw.Draw(mask)
        draw.ellipse(ellipse + size, fill=0)
        img = Image.open(img)
        output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
        output.putalpha(500)
        output.paste(0, mask=mask)
        output.convert("P", palette=Image.ADAPTIVE)
        buffer = io.BytesIO()
        output.save(buffer, format="png")
        return discord.File(io.BytesIO(buffer.getvalue()), "circular.png")

    @commands.command(name="rounden", aliases=["circle", "round", "circular"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def _rounden(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.session.get(str(url))
        img = await img.read()
        res = await self.rounden(io.BytesIO(img), (0, 0))
        em = discord.Embed(color=get_random_color())
        em.set_image(url="attachment://circular.png")
        await ctx.send(file=res, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def pixel(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.pixel(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command(aliases=["amhu"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def allmyhomiesuse(self, ctx, bad: str, good: str):

        img = await self.bot.dagpi.image_process(
            asyncdagpi.ImageFeatures.retro_meme(),
            url="https://media.discordapp.net/attachments/698057848449400832/855803039649366036/dee.png",
            top_text=f"Fuck {bad}",
            bottom_text=f"All My Homies use {good}",
        )
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def retromeme(self, ctx, top: str, bottom: str, url: str = None):
        url = await get_image(ctx, url)

        img = await self.bot.dagpi.image_process(
            asyncdagpi.ImageFeatures.retro_meme(),
            url=url,
            top_text=top,
            bottom_text=bottom,
        )
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def modernmeme(self, ctx, top: str, bottom: str, url: str = None):
        url = await get_image(ctx, url)

        img = await self.bot.dagpi.image_process(
            asyncdagpi.ImageFeatures.retro_meme(),
            url=url,
            top_text=top,
            bottom_text=bottom,
        )
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def america(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.america(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def triggered(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.triggered(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.gif")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.gif")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def colors(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.colors(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.gif")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.gif")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def communism(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.communism(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.gif")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.gif")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def wasted(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.wasted(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def fiveguys(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
        member2: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)
        url2 = await get_image(ctx, member2)

        img = await self.bot.dagpi.image_process(
            asyncdagpi.ImageFeatures.five_guys_one_girl(), url=str(url), url2=str(url2)
        )
        file = discord.File(img.image, f"{ctx.command.name}.gif")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.gif")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def whygay(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
        member2: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)
        url2 = await get_image(ctx, member2)

        img = await self.bot.dagpi.image_process(
            asyncdagpi.ImageFeatures.why_are_you_gay(), url=str(url), url2=str(url2)
        )
        file = discord.File(img.image, f"{ctx.command.name}.gif")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.gif")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def invert(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.invert(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bomb(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.bomb(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.gif")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.gif")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def sobel(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.sobel(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def triangle(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.triangle(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def angel(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.angel(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command(aliases=["s8n"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def satan(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.satan(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def delete(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.delete(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def fedora(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.fedora(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command(aliases=["hitler", "wth"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def worsethanhitler(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.hitler(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def wanted(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.wanted(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command(aliases=["ytcomment"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def youtubecomment(self, ctx, member: discord.Member, *, text):

        img = await self.bot.dagpi.image_process(
            asyncdagpi.ImageFeatures.youtube(),
            url=get_image(ctx, member),
            username=member.display_name,
            text=text,
        )
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command(name="discord")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _discord(self, ctx, member: discord.Member, *, text):

        img = await self.bot.dagpi.image_process(
            asyncdagpi.ImageFeatures.discord(),
            url=str(member.avatar.with_format("png")),
            username=member.display_name,
            text=text,
        )
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def jail(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        if member is None:
            if ctx.message.attachments:
                if (
                    ctx.message.attachments[0].url.endswith("png")
                    or ctx.message.attachments[0].url.endswith("jpg")
                    or ctx.message.attachments[0].url.endswith("jpeg")
                    or ctx.message.attachments[0].url.endswith("webp")
                ):
                    url = ctx.message.attachments[0].proxy_url or ctx.message.attachments[0].url
                else:
                    url = ctx.author.with_format("png")
            else:
                url = ctx.author.with_format("png")
        else:
            url = member.with_format("png")

            img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.jail(), url=str(url))
            file = discord.File(img.image, f"{ctx.command.name}.png")
            em = discord.Embed(color=get_random_color())
            em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def pride(
        self,
        ctx,
        flag: str = "gay",
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.pride(), url=str(url), flag=flag)
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def trash(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.trash(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def magik(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.magik(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def paint(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.paint(), url=str(url))
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def captcha(
        self,
        ctx,
        text: str,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        img = await self.bot.dagpi.image_process(asyncdagpi.ImageFeatures.captcha(), url=str(url), text=text)
        file = discord.File(img.image, f"{ctx.command.name}.png")
        em = discord.Embed(color=get_random_color())
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(file=file, embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def clyde(self, ctx, *, message):

        res = await self.bot.session.get(f"https://nekobot.xyz/api/imagegen?type=clyde", params={"text": message})
        res = await res.json()
        res = res["message"]
        em = discord.Embed(color=get_random_color())
        em.set_image(url=res)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def stickbug(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        res = await self.bot.session.get(f"https://nekobot.xyz/api/imagegen?type=stickbug&url={url}")
        res = await res.json()
        res = res["message"]
        img = await self.bot.session.get(res)
        img = await img.read()
        await ctx.send(
            file=discord.File(io.BytesIO(img), filename="stickbug.mp4"),
            mention_author=False,
        )

    @commands.command(aliases=["cmm"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def changemymind(self, ctx, *, message):
        message = message.replace(" ", "%20")

        res = await self.bot.session.get(f"https://nekobot.xyz/api/imagegen?type=changemymind", params={'text': message})
        res = await res.json()
        res = res["message"]
        em = discord.Embed(color=get_random_color())
        em.set_image(url=res)
        await ctx.send(embed=em)

    @commands.command(aliases=["phc", "pornhubcomment"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def phcomment(self, ctx, member: discord.Member, *, message):

        res = await self.bot.session.get(
            f"https://nekobot.xyz/api/imagegen?type=phcomment&image={member.avatar_url_as(format='png')}&username={member.display_name}", params={'text':message}
        )
        res = await res.json()
        res = res["message"]
        em = discord.Embed(color=get_random_color())
        em.set_image(url=res)
        await ctx.send(embed=em)

    @commands.command(aliases=["iphonex"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def iphone(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        res = await self.bot.session.get(f"https://nekobot.xyz/api/imagegen?type=iphonex&url={url}")
        res = await res.json()
        image = res["message"]
        em = discord.Embed(color=get_random_color())
        em.set_image(url=image)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def jpeg(
        self,
        ctx,
        member: typing.Union[discord.Emoji, discord.PartialEmoji, discord.Member, str] = None,
    ):
        url = await get_image(ctx, member)

        res = await self.bot.session.get(f"https://nekobot.xyz/api/imagegen?type=jpeg&url={url}")
        res = await res.json()
        image = res["message"]
        em = discord.Embed(color=get_random_color())
        em.set_image(url=image)
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Image(bot))

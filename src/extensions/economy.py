import random

import discord
from discord.ext import commands
from utils.functions import get_random_color, read_file


class Economy(commands.Cog):
    """Economy commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.celebs = read_file("assets/data/celebs.json")

    async def get_account(self, user):
        info = await self.db.fetchrow(
            """
            SELECT *
            FROM economy
            WHERE user_id=$1
            """,
            user,
        )
        if info is None:
            await self.db.execute(
                """
                    INSERT INTO economy (user_id, wallet, bank, inventory)
                    VALUES ($1, $2, $3, $4)
                """,
                user,
                0,
                0,
                "{}",
            )
            return await self.db.fetchrow(
                """
                SELECT *
                FROM economy
                WHERE user_id=$1
                """,
                user,
            )
        else:
            return info

    @commands.command(aliases=["bal"])
    async def balance(self, ctx, user: discord.User = None):
        user = user or ctx.author
        info = await self.get_account(user.id)
        e = discord.Embed(title=user.name + "'s balance", color=get_random_color())
        e.add_field(name="Wallet", value=info["wallet"])
        e.add_field(name="Bank", value=info["bank"])
        e.add_field(name="Total", value=info["bank"] + info["wallet"])
        await ctx.send(embed=e)

    @commands.command(aliases=["with"])
    async def withdraw(self, ctx, amount: int):
        info = await self.get_account(ctx.author.id)
        if amount == "all":
            amount = info["bank"]
        else:
            try:
                amount = int(amount)
            except ValueError:
                return await ctx.send("Invalid amount")
        if amount > info["bank"]:
            await ctx.send("Can't withdraw more than you have in your bank")
            return
        bank = info["bank"] - amount
        wallet = info["wallet"] + amount
        await self.db.execute(
            """
                UPDATE economy
                SET wallet = $2,
                    bank   = $3
                WHERE user_id = $1;
                """,
            ctx.author.id,
            wallet,
            bank,
        )
        await ctx.send(f"{amount} coins withdrawn")

    @commands.command(aliases=["dep"])
    async def deposit(self, ctx, amount):
        info = await self.get_account(ctx.author.id)
        if amount == "all":
            amount = info["wallet"]
        else:
            try:
                amount = int(amount)
            except ValueError:
                return await ctx.send("Invalid amount")
                return

        if amount > info["wallet"]:
            await ctx.send("Can't withdraw more than you have in your wallet")
            return
        bank = info["bank"] + amount
        wallet = info["wallet"] - amount
        await self.db.execute(
            """
                UPDATE economy
                SET wallet = $2,
                    bank   = $3
                WHERE user_id = $1;
                """,
            ctx.author.id,
            wallet,
            bank,
        )
        await ctx.send(f"{amount} coins deposited")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def beg(self, ctx):
        if random.random() < 0.5:
            return await ctx.send(random.choice(self.celebs) + " said he doesn't want to give you money")
        amount = random.randint(1, 500)
        info = await self.get_account(ctx.author.id)
        wallet = info["wallet"] + amount
        celeb = random.choice(self.celebs)
        await self.db.execute(
            """
                UPDATE economy
                SET wallet = $2
                WHERE user_id = $1;
                """,
            ctx.author.id,
            wallet,
        )
        await ctx.send(f"{celeb} gave you {amount} coins")

    @commands.command(aliases=["rob"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def steal(self, ctx, *, user: discord.User):
        author_account = await self.get_account(ctx.author.id)
        user_account = await self.get_account(user.id)
        if user_account["wallet"] < 1:
            await ctx.send(f"Ah, {user.name} has no money.send(big rip")
            return
        if user_account["wallet"] < 1000:
            amount = random.randint(1, user_account["wallet"])
        else:
            amount = random.randint(1, 1000)
        wallet = author_account["wallet"] + amount
        await self.db.execute(
            """
                UPDATE economy
                SET wallet = $2
                WHERE user_id = $1;
                """,
            ctx.author.id,
            wallet,
        )
        wallet = user_account["wallet"] - amount
        await self.db.execute(
            """
                UPDATE economy
                SET wallet = $2
                WHERE user_id = $1;
                """,
            user.id,
            wallet,
        )
        await ctx.send(f"You stole {amount} coins from {user.name}")

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def give(self, ctx, amount: int, *, user: discord.User):
        user_account = await self.get_account(ctx.author.id)
        author_account = await self.get_account(user.id)
        if user_account["wallet"] < 1:
            await ctx.send(f"You have no money to give")
            return
        if amount > user_account["wallet"]:
            await ctx.send("You don't have enough money")
            return
        wallet = author_account["wallet"] + amount
        await self.db.execute(
            """
                UPDATE economy
                SET wallet = $2
                WHERE user_id = $1;
                """,
            user.id,
            wallet,
        )
        wallet = user_account["wallet"] - amount
        await self.db.execute(
            """
                UPDATE economy
                SET wallet = $2
                WHERE user_id = $1;
                """,
            ctx.author.id,
            wallet,
        )
        await ctx.send(f"You gave {amount} coins to {user.name}")


def setup(bot):
    """Adds the cog to the bot"""
    if hasattr(bot, "db"):
        bot.add_cog(Economy(bot))

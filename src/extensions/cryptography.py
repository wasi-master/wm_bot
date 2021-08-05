import base64 as base64module
from typing import Union

import discord
from discord.ext import commands


class BinaryConverter(commands.Converter):
    async def convert(self, ctx, string):
        string = "".join(i for i in string if i in ("0", "1"))
        try:
            return int(string, 2)
        except ValueError:
            raise commands.BadArgument("Invalid binary.")


class Cryptography(commands.Cog):
    """Encoding and Decoding text releated commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        aliases=["b64"],
        invoke_without_command=True,
    )
    async def base64(self, ctx):
        """Command for encoding and decoding text from and to [base64](https://en.wikipedia.org/wiki/Base64)"""
        if ctx.invoked_subcommand is None:
            await ctx.send("You should use a subcommand, for example: `b64 encode <text>`")

    @base64.command(name="encode", aliases=["e"])
    async def base64_encode(self, ctx, *, text: commands.clean_content):
        """Encode text to base64"""
        encoded_bytes = base64module.b64encode(text.encode("utf-8"))
        encoded_str = str(encoded_bytes, "utf-8")
        await ctx.send(encoded_str)

    @base64.command(name="decode", aliases=["d"])
    async def base64_decode(self, ctx, text: commands.clean_content):
        """Decode text from base64"""
        decoded_bytes = base64module.b64decode(text)
        decoded_str = decoded_bytes.decode("ascii")
        await ctx.send(decoded_str)

    @commands.command(aliases=["bin"])
    async def binary(self, ctx, *, text: Union[int, str]):
        """Converts text to binary, can take both a number or a string"""
        if isinstance(text, str):
            encoded_str = " ".join(map(lambda x: bin(x).lstrip("0b"), bytearray(text.encode("utf-8"))))
        else:
            encoded_str = f"{text:08b}"
            encoded_str = " ".join([encoded_str[i : i + 8] for i in range(0, len(encoded_str), 8)])
        await ctx.send(embed=discord.Embed(description=f"{encoded_str}"))

    @commands.command(aliases=["unbin"])
    async def unbinary(self, ctx, *, binary_number: BinaryConverter):
        """Converts binary to text, the input needs to be encoded in binary format"""
        decoded_bytes = binary_number.to_bytes((binary_number.bit_length() + 7) // 8, "big")
        decoded_str = decoded_bytes.decode("utf-8")
        await ctx.send(embed=discord.Embed(description=f"**Number**: {binary_number}\n**Text**: {decoded_str}"))


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Cryptography(bot))

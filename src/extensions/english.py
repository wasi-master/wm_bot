import json

import discord
from discord.ext import commands

from utils.converters import LanguageConverter
from utils.errors import NoAPIKey
from utils.functions import load_json
from utils.paginator import Paginator

class TranslateFlags(commands.FlagConverter, delimiter=" ", case_insensitive=True):
    lang: LanguageConverter = commands.flag(name="lang", default="en")
    text: str = commands.flag(positional=True)

class English(commands.Cog):
    """Commands for the english language"""

    def __init__(self, bot):
        self.bot = bot
        # We set the variable to the bot since it is gonna be used by our converter
        bot.language_codes = load_json("assets/data/language_codes.json")

    @commands.command(aliases=["def", "df"])
    @commands.bot_has_permissions(use_external_emojis=True)
    async def define(self, ctx, word: str):
        """Sends the definition of a word"""
        # getting the api key
        try:
            token = self.bot.api_keys["owlbot"]
        except KeyError:
            raise NoAPIKey
        # Doing the request
        heds = {"Authorization": f"Token {token}"}
        async with self.bot.session.get(f"https://owlbot.info/api/v4/dictionary/{word}?format=json", headers=heds) as r:
            text = await r.text()
        fj = json.loads(text)
        # Validation
        definitions = fj["definitions"]
        if len(definitions) == 0:
            await ctx.send("Word not found")
        # Formatting the result
        embeds = []
        for definition in definitions:
            emb = discord.Embed(title=fj["word"], description=definition["definition"])
            emb.add_field(
                name="Example",
                value=definition["example"].replace("<b>", "**").replace("</b>", "**"),
                inline=False,
            )
            emb.add_field(name="Pronunciation", value=fj["pronunciation"], inline=False)
            if definition["image_url"]:
                emb.set_image(url=definition["image_url"])
            embeds.append(emb)
        # Sending the results
        pag = Paginator(embeds, "Definition")
        await pag.start(ctx)

    @commands.command(aliases=["tr"])
    async def translate(self, ctx, *, flags: TranslateFlags):
        """Translates a text to another language if specified, defaults to English"""
        lang = flags.lang or "en"
        text = flags.text
        if not text:
            return await ctx.send("You need to specify text to translate")

        result = await ctx.bot.translate_api.translate(text, targetlang=lang)
        # We get the full language names
        languageconverter = LanguageConverter()
        source = languageconverter.convert(ctx, result.src)
        destination = languageconverter.convert(ctx, result.dest)

        embed = discord.Embed(title=f"Translation", description=result.text, color=0x2F3136)
        if result.text != result.pronunciation:
            embed.add_field(name="Pronunciation", value=result.pronunciation)
        embed.set_footer(text=f"Translated from {source.split(';')[0]} to {destination.split(';')[0]}")
        await ctx.send(embed=embed)


async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(English(bot))

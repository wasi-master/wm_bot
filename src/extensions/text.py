import asyncio
import difflib
import os
import random
import re
import string
import unicodedata
import urllib

from rich import print as rprint
import discord
import gtts
import humanize
from better_profanity import profanity
from discord.ext import commands
from discord.ext.commands import BucketType
import uwuify
from utils.functions import levenshtein_match_calc, load_json

def tts(lang: str, text: str):
    """Generates a tts file"""
    speech = gtts.gTTS(text=text, lang=lang, slow=False)
    speech.save("tts.mp3")
    return


# FIXME: Should use 2.0 flags
class Font(commands.Converter):
    """A font converter"""
    async def convert(self, ctx, argument):
        try:
            if "--" in argument:
                return re.findall(r"--.+\s", argument)[0].strip()
        except Exception as exc:
            raise commands.BadArgument("Invalid Font")
        else:
            raise commands.BadArgument("No Font")


def show_diff(seqm: difflib.SequenceMatcher) -> str:
    """Unify operations between two compared strings

    Parameters
    ----------
    seqm : difflib.SequenceMatcher
        sequencematcher instance whose a & b are strings

    Returns
    -------
    str
        unified string
    """
    output = []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == "equal":
            output.append(seqm.a[a0:a1][0])
        elif opcode == "insert":
            output.append(f"**( +`{seqm.a[b0:b1][0]}` )**")
        elif opcode == "delete":
            output.append(f"**( ?`{seqm.b[a0:a1][0]}` )**")
        elif opcode == "replace":
            output.append(f"**__( `{seqm.b[b0:b1][0]}` -> `{seqm.a[a0:a1][0]}` )__**")
        else:
            output.append(seqm.a[a0:a1][0])
    return " ".join(output)


class Text(commands.Cog):
    """Commands that take a input as text and send a output as text"""

    def __init__(self, bot):
        self.bot = bot
        self.marks = list(map(chr, range(768, 879)))
        self.morse_dict = load_json("assets/data/morse_code.json")
        self.abs = load_json("assets/data/abs.json")

        bot.loop.create_task(self.get_words())

    def _zalgo(self, text: str) -> str:
        """Converts a text to zalgo

        Parameters
        ----------
        text : str
            The text to zalgo-fy

        Returns
        -------
        str
            The zalgo-fied text
        """
        words = text.split()
        zalgo = " ".join(
            "".join(c + "".join(random.choice(self.marks) for _ in range(i // 2 + 1)) * c.isalnum() for c in word)
            for i, word in enumerate(words)
        )
        return zalgo

    async def get_words(self):
        """Gets the words and saves them to self.words"""
        async with self.bot.session.get(
            "https://gist.githubusercontent.com/h3xx/1976236/raw/bbabb412261386673eff521dddbe1dc815373b1d/wiki-100k.txt"
        ) as resp:
            self.words = (await resp.text()).splitlines()[25:]
        rprint(f"[green]Loaded[/] [yellow]{len(self.words):,}[/] [green]words[/]")


    @commands.command(aliases=["trc"])
    async def typeracer(self, ctx):
        """See your typing speed"""

        def check(msg):
            return msg.channel == ctx.channel and msg.author == ctx.author

        # Each text should be between 30 and 40 words
        text_length = random.randint(30, 40)
        words = random.sample(self.words, text_length)
        # We filter the profane words out
        words = list(filter(lambda m: len(m) > 2 and not profanity.contains_profanity(m), words))

        # This is what the use should type
        correct_text = " ".join(words)

        # We add some security measures to the message that is sent
        send_text = ""
        for word in words:
            send_text += word + (random.choice(list(map(chr, range(8192, 8208)))) + " ")

        # We send the message
        bot_message = await ctx.send(f"__**Type the words given below**__\n```{send_text}```")


        start = bot_message.created_at
        try:
            message = await self.bot.wait_for("message", check=check, timeout=120)
        except asyncio.TimeoutError:
            return await ctx.send(f"{ctx.author.mention} wow you are slowest typer ever to be alive")
        end = message.created_at

        # We get the accurary of the user
        acc = levenshtein_match_calc(message.content, correct_text)
        # If the accuracy is less than 70% then the user is most likely trolling
        if acc < 70:
            return await message.reply("why didn't you write the whole thing? If you can't write why did you use the command 😒?")

        # We calculate his time
        time = (end - start).total_seconds()

        # Some more security measures
        if any(i in message.content for i in list(map(chr, range(8192, 8208)))):
            return await ctx.send("Imagine cheating bruh")
        # The user probably can't type 30-40 words in 12 secs (150-200 WPM)
        if time < 12:
            return await ctx.send("Imagine cheating bruh")

        # We find the user's mistakes
        mistakes = []
        given_words = message.content.split()
        matcher = difflib.SequenceMatcher(None, message.content.split(" "), correct_text.split(" "))
        ratio = matcher.ratio()
        right = []
        for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
            if opcode == "equal":
                right.append(matcher.a[a0:a1][0])
            elif opcode in ("delete", "replace"):
                if matcher.b[a0:a1]:
                    mistakes.append(matcher.b[a0:a1][0])

        # We finally calculate his words per minute
        wpm = (len(message.content) / 5) / (time / 60)
        right_words = len(correct_text.split()) - len(mistakes)
        fixed_wpm = wpm - len(mistakes)

        # We make a string to show as the mistakes
        if len(mistakes) < 8 and len(mistakes) > 0:
            mistk = ", ".join(mistakes)
        elif len(mistakes) > 8:
            mistk = ", ".join(mistakes[:8]) + "..."
        else:
            mistk = "None, wow"

        message = await ctx.send(
            f"```ini"
            f"[WPM] {round(wpm, 3)}"
            f"[FIXED WPM] {round(fixed_wpm, 3)}"
            f"[TIME] {time} SECONDS"
            f"[ACCURACY] {round(ratio*100, 3)}%"
            f"[CORRECT WORDS] {right_words}"
            f"[MISTAKES] {mistk}"
            f"[WORDS GIVEN] {len(words)}"
            f"[WORDS FROM {ctx.author.display_name.upper()}] {len(given_words)}"
            f"[CHARACTERS GIVEN] {len(correct_text)}"
            f"[CHARACTERS FROM {ctx.author.display_name.upper()}] {len(message.content)}"
            f"```"
            f"React with 🤔 to see where your mistakes are."
        )
        await message.add_reaction("🤔")

        try:
            await self.bot.wait_for(
                "reaction_add",
                check=lambda r, u: u.id == ctx.author.id and str(r.emoji) == "🤔" and r.message.id == message.id,
                timeout=30,
            )
        except asyncio.TimeoutError:
            await message.remove_reaction("🤔", ctx.me)
        else:
            await ctx.send(f"{ctx.author.mention}\n{show_diff(matcher)}")

    @commands.command()
    async def randomcase(self, ctx, inp):
        """Converts the given input to a random case

        For example "hello my name is wasi" can become "hELlO mY NamE is WaSI"
        """
        case = [str.upper, str.lower]
        await ctx.send("".join(case[round(random.random())](s) for s in inp))

    @commands.command()
    @commands.cooldown(1, 15, BucketType.default)
    async def hastebin(self, ctx, data):
        """Pastes the given data to hastebin and returns the link"""
        data = bytes(data, "utf-8")

        async with self.bot.session.post("https://hastebin.com/documents", data=data) as response:
            res = await response.json()
            key = res["key"]
            url = f"https://hastebin.com/{key}"

        embed = discord.Embed(title="Paste Successful", description=url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 15, BucketType.channel)
    async def spoiler(self, ctx, *, text: str):
        """Spoilers a text letter by letter"""
        result = "".join(f"||{i}||" for i in text)

        if len(result) > 2000:
            return await ctx.send("Too long")
        if not result:
            return await ctx.send("Empty Result")

        await ctx.send(f"```{result}```")

    @commands.command()
    async def reverse(self, ctx, *, text: str):
        """Reverses a text"""
        result = "".join(reversed(text))

        embed = discord.Embed(
            title="Reverse",
            description=f"**Original**:\n{text}\n**Reversed**:\n{result}",
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["bsr"])
    @commands.cooldown(1, 15, BucketType.channel)
    async def boxspoilerrepeat(self, ctx, width: int, height: int, *, text: str):
        """Box shaped spoilers and repeats a text"""
        result = "".join(f"||{text}||" * width + "\n" for _ in range(height))

        if len(result) > 2000:
            return await ctx.send("Too long")
        if not result:
            return await ctx.send("Empty Result")

        await ctx.send(f"```{result}```")

    @commands.command(description="Repeats a text")
    @commands.cooldown(1, 15, BucketType.channel)
    async def repeat(self, ctx, amount: int, *, text: str):
        result = text * amount

        if len(result) > 2000:
            await ctx.send("Text too long")

        await ctx.send(f"```{result}```", delete_after=10)

    @commands.command(description="Morse code :nerd:")
    async def morse(self, ctx, *, text: str):
        cipher = " ".join(self.morse_dict[char] for char in text.upper())
        await ctx.send(embed=discord.Embed(title=str(ctx.author), description=cipher, color=0x2F3136))

    @commands.command(description="English to morse")
    async def unmorse(self, ctx, *, text: str):
        # HACK: I don't know how this works but I need to to make it cleaner
        message = text
        message += " "
        decipher = ""
        citext = ""
        for letter in message:
            if letter != " ":
                i = 0
                citext += letter.upper()
            else:
                i += 1
                if i == 2:
                    decipher += " "
                else:
                    decipher += list(self.morse_dict.keys())[list(self.morse_dict.values()).index(citext)]
                    citext = ""
        await ctx.send(embed=discord.Embed(title=str(ctx.author), description=decipher, color=0x2F3136))

    @commands.command(
        aliases=["avs", "abs", "whatdoesitmean" "wdim"],
    )
    async def abbreviations(self, ctx, text: commands.clean_content):
        """See the meaning of a texting abbreviation

        Like "idk" means "I don't know"
        """
        if not text.upper() in self.abs:
            embed = discord.Embed(
                title=f"Abbreviation for {text} not found",
                description=f"Did you mean any of these?\n{', '.join(difflib.get_close_matches(text, abs_str, n=5, cutoff=0.2))}",
                color=0x2F3136,
            )
            return await ctx.send(embed=embed)
        result = self.abs[text.upper()]
        embed = discord.Embed(title=text, description=result, color=0x2F3136)
        await ctx.send(embed=embed)


    @commands.command(aliases=["tts"])
    @commands.cooldown(1, 5, BucketType.user)
    async def texttospeech(self, ctx, lang: str, *, text: str):
        """Converts some text to speech (TTS)"""
        msg = await ctx.send(f"Generating {self.bot.get_custom_emoji('load.typing')}")
        await self.bot.loop.run_in_executor(None, tts, lang, text)
        await ctx.send(f"{ctx.author.mention} Here you go:", file=discord.File("tts.mp3"))
        await msg.delete()

        # We delete the file that gtts created
        os.remove("tts.mp3")

    @commands.command(
        aliases=["chrinf", "unicode", "characterinfo"],
    )
    async def charinfo(self, ctx, *, characters: str):
        """Sends information about a character 🤓"""
        def to_string(c):
            #  l.append("a")
            digit = f"{ord(c):x}"
            name = unicodedata.name(c, "Name not found.")
            return f"`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>"

        msg = "\n".join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send("Output too long to display.")
        await ctx.send(msg)

    @commands.command(aliases=["fancy", "emf", "banner"], description="Emojify a text")
    async def emojify(self, ctx, *, text: str):
        list_ = []
        fixed = {
            "?": ":grey_question:",
            "!": ":grey_exclamation:",
            "#": ":hash:",
            "*": ":asterisk:",
            "∞": ":infinity:",
        }

        for word in text:
            if word in list(string.ascii_letters):
                list_.append(f":regional_indicator_{word.lower()}:")
            elif word.isdigit():
                list_.append(f":{humanize.apnumber(word)}:")
            elif word == " ":
                list_.append("   ")
            elif word in fixed:
                list_.append(fixed[word])

        result = " ".join(list_)

        if len(result) > 2000:
            return await ctx.send("Too long to display")

        await ctx.send(result)


    @commands.command(aliases=["cc", "charcount"])
    async def charactercount(self, ctx, *, text):
        await ctx.send(len(text))


    @commands.command(name="uwuify", aliases=["uwu"], description="uwuifies a given text")
    async def uwuify_(self, ctx, *, text: commands.clean_content):
        await ctx.send(uwuify.uwu(text))

    @commands.command()
    async def ascii(self, ctx, *, text: str = None):
        if text is None:
            await ctx.channel.send(
                f"Usage: `{ctx.prefix}ascii [font (optional)] [text]`\n(font list at http://artii.herokuapp.com/fonts_list)"
                )
            return

        # Get list of fonts
        fonturl = "http://artii.herokuapp.com/fonts_list"
        async with self.bot.session.get(fonturl) as r:
            response = await r.text()
        fonts = response.split()

        font = None
        # Split text by space - and see if the first word is a font
        parts = text.split()
        if len(parts) > 1:
            # We have enough entries for a font
            if parts[0] in fonts:
                # We got a font!
                font = parts[0]
                text = " ".join(parts[1:])

        url = "http://artii.herokuapp.com/make?{}".format(urllib.parse.urlencode({"text": text}))
        if font:
            url += "&font={}".format(font)
        async with self.bot.session.get(url) as r:
            response = await r.text()
        await ctx.channel.send("```Markup\n{}```".format(response))

    @commands.command()
    async def zalgo(self, ctx, *, message):
        """Ỉ s̰hͨo̹u̳lͪd͆ r͈͍e͓̬a͓͜lͨ̈l̘̇y̡͟ h͚͆a̵͢v͐͑eͦ̓ i͋̍̕n̵̰ͤs͖̟̟t͔ͤ̉ǎ͓͐ḻ̪ͨl̦͒̂ḙ͕͉d͏̖̏ ṡ̢ͬö̹͗m̬͔̌e̵̤͕ a̸̫͓͗n̹ͥ̓͋t̴͍͊̍i̝̿̾̕v̪̈̈͜i̷̞̋̄r̦̅́͡u͓̎̀̿s̖̜̉͌...""" # pylint: disable=line-too-long
        words = message.split()
        try:
            iterations = len(words) - 1
            words = words[:-1]
        except IndexError:
            iterations = 1

        # Maximum iteration is 100 times and minimum iteration is 1 time
        iterations = max(min(iterations, 100),1)

        zalgo = " ".join(words)
        for i in range(iterations):
            if len(zalgo) > 2000:
                break
            zalgo = self._zalgo(zalgo)

        zalgo = zalgo[:2000]
        await ctx.send(zalgo)


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Text(bot))

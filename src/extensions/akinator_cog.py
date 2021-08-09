"""Akinator Cog"""
from typing import Optional

import discord
from discord.ext import commands
from utils.functions import button_from_json, get_p, print_error
from utils.paginator import Paginator


class AkinatorButton(discord.ui.Button):
    """A class for a button for akinator"""

    async def callback(self, interaction):
        # If we have progressed more that 50% and less thatn 80%,
        # We want to disable the answer button
        if 50 < self.view.bot.aki.progression < 80:
            # With this we find the button based on the label. this function is
            # a custom function that is not defined in the standard discord.ui.View
            answer_button = await self.view.find_button("Who is it?")
            answer_button.disabled = False
        elif self.view.bot.aki.progression > 80:
            # If we have progressed more than 80%. We end the game because
            # the current guess is probably close enough
            await self.view.win()
            # The return here just stops the code from going further
            return

        # They want to end the session
        if self.label == "End Session":
            await interaction.response.edit_message(content="Stopped", embed=None, view=None)
            self.view.stop()
            return
        # They want to know who is it
        elif self.label == "Who is it?":
            await self.view.win(prepared=False)
            return
        # They want to go back
        elif self.label == "Go Back":
            self.view.question = await self.view.bot.aki.back()
        # They answered
        else:
            # We add their answer to the list of answers
            self.view.all_questions.append({"question": self.view.question, "answered": self.label})
            self.view.question = await self.view.bot.aki.answer(self.label)
            # We enable the back button since now there is
            # an answer that they can go back to if they want
            back_button = await self.view.find_button("Go Back")
            back_button.disabled = False

        # User went all the way back. So we want to disable the back button
        if self.view.bot.aki.step == 0:
            back_button = await self.view.find_button("Go Back")
            back_button.disabled = True

        emb = await self.view.get_embed()
        await interaction.response.edit_message(embed=emb, view=self.view)


class AkinatorView(discord.ui.View):
    """ok."""

    def __init__(self, question, ctx):
        super().__init__()
        self.question = question
        self.ctx = ctx
        self.bot = ctx.bot
        self.message = None
        self.all_questions = []

        emojis = self.bot.emoji_config
        buttons = [
            {
                "label": "Yes",
                "style": discord.ButtonStyle.green,
                "emoji": emojis.validation.green_tick or "✅",
                "row": 0,
            },
            {
                "label": "No",
                "style": discord.ButtonStyle.red,
                "emoji": emojis.validation.red_tick or "❌",
                "row": 0,
            },
            {"label": "I don't know", "style": discord.ButtonStyle.gray, "row": 1},
            {"label": "Probably", "style": discord.ButtonStyle.blurple, "row": 2},
            {"label": "Probably Not", "style": discord.ButtonStyle.blurple, "row": 2},
            {
                "label": "Go Back",
                "style": discord.ButtonStyle.red,
                "emoji": "\u25c0\ufe0f",
                "row": 3,
                "disabled": True,
            },
            {
                "label": "End Session",
                "style": discord.ButtonStyle.red,
                "emoji": "⏹️",
                "row": 3,
            },
            {
                "label": "Who is it?",
                "style": discord.ButtonStyle.gray,
                "emoji": "🤔",
                "disabled": True,
                "row": 4,
            },
        ]
        for button in buttons:
            self.add_item(button_from_json(button, cls=AkinatorButton))

    async def find_button(self, button: str) -> Optional[discord.ui.Button]:
        """Finds a button in the view

        Parameters
        ----------
        button : str
            The label of the button to find

        Returns
        -------
        discord.ui.Button
            The button that was found, can be None
        """
        return discord.utils.get(self.children, label=button)

    async def get_embed(self) -> discord.Embed:
        """Maked a embed with all the current stats

        Returns
        -------
        discord.Embed
            The embed that was made
        """
        progressbar = get_p(self.bot.aki.progression, prefix="```", suffix="```", length=30, decimals=4)
        embed = discord.Embed(title="Akinator", description=f"{self.question}")
        embed.add_field(name="Progress", value=progressbar, inline=False)
        embed.set_footer(text=f"Question no: {self.bot.aki.step+1}")
        if self.all_questions:
            prev_ques = self.all_questions[-1]
            embed.add_field(
                name="Previous",
                value=f"Question: {prev_ques['question']}\nAnswered: {prev_ques['answered']}",
                inline=False,
            )
        return embed

    async def interaction_check(self, interaction):
        """Checks if the interaction was from the person that invoked the command"""
        return interaction.user == self.ctx.author

    async def win(self, prepared=True):
        """Wins the game

        Parameters
        ----------
        prepared : bool, optional
            Whether the user answered questions to get the answer or not, by default True
            If False, it means the user clicked the button to get the answer
        """
        aki = self.bot.aki
        await aki.win()
        if prepared:
            embed = discord.Embed(
                title=f"You thought of {aki.first_guess['name']} ({aki.first_guess['proba']}% chance)",
                description=f"{aki.first_guess['description']}\n\n Ranking: {aki.first_guess['ranking']}",
            )
            embed.set_image(url=aki.first_guess["absolute_picture_path"])
            await self.ctx.reply(embed=embed)
        else:
            embeds = []
            for num, guess in enumerate(aki.guesses):
                # We have multiple guesses so we loop through them and
                # make a embed and add the embed to a list so we can paginate
                embed = discord.Embed(
                    title=f"You thought of {guess['name']} ({guess['proba']}% chance)",
                    description=f"{guess['description']}\n\n Ranking: {guess['ranking']}",
                )
                embed.set_author(name=f"{num}.")
                embed.set_image(url=guess["absolute_picture_path"])
                embeds.append(embed)
            # This paginator class is custom made and defined in utils
            paginator = Paginator(embeds)
            paginator.start(self.ctx)

        self.clear_items()
        self.stop()


class Akinator(commands.Cog):
    """The beloved Akinator game"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["aki"], extras={"image": "https://i.imgur.com/r6086QT.gif"})
    @commands.max_concurrency(1)
    @commands.bot_has_permissions(use_external_emojis=True)
    async def akinator(self, ctx):
        """A command to play a game of akinator"""
        game = await self.bot.aki.start_game(client_session=self.bot.session)
        view = AkinatorView(game, ctx)
        view.message = await ctx.send(embed=await view.get_embed(), view=view)


def setup(bot):
    """Adds the cog to the bot"""
    try:
        import akinator # pylint: disable=import-outside-toplevel
    except ImportError:
        print_error(
            "You don't have akinator installed. please install all "
            "the required packages by using `pip install -r requirements.txt`"
        )
    else:
        del akinator
        bot.add_cog(Akinator(bot))

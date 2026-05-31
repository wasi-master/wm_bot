"""File for storing the Paginator"""
import asyncio
from typing import List, Optional

import discord
from discord.ext import commands

from .functions import get_custom_emoji

__all__ = "Paginator"


class Paginator(discord.ui.View):
    """A paginator using discord.ui.View with buttons.

    Replaces the old discord.ext.menus based paginator.
    """

    def __init__(self, embeds: List[discord.Embed], page_name="Page", *, timeout: float = 180.0):
        """Initializes the paginator

        Parameters
        ----------
        embeds : List[discord.Embed]
            A list of embeds to paginate from
        page_name : str, optional
            The text to display on the footer of the embed, by default "Page"
        timeout : float, optional
            How long the paginator should be active for, by default 180 seconds
        """
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.page_name = page_name
        self.message: Optional[discord.Message] = None
        self.ctx: Optional[commands.Context] = None

        # Try to load custom emojis, fall back to unicode if they fail
        try:
            self._first_emoji = get_custom_emoji("paginator.first")
        except Exception:
            self._first_emoji = "⏮️"
        try:
            self._prev_emoji = get_custom_emoji("paginator.previous")
        except Exception:
            self._prev_emoji = "◀️"
        try:
            self._pause_emoji = get_custom_emoji("paginator.pause")
        except Exception:
            self._pause_emoji = "⏸️"
        try:
            self._next_emoji = get_custom_emoji("paginator.next")
        except Exception:
            self._next_emoji = "▶️"
        try:
            self._last_emoji = get_custom_emoji("paginator.last")
        except Exception:
            self._last_emoji = "⏭️"
        try:
            self._numbered_emoji = get_custom_emoji("paginator.numbered")
        except Exception:
            self._numbered_emoji = "🔢"
        try:
            self._stop_emoji = get_custom_emoji("paginator.stop")
        except Exception:
            self._stop_emoji = "⏹️"

        # Set button emojis
        self.first_page_button.emoji = self._first_emoji
        self.previous_page_button.emoji = self._prev_emoji
        self.pause_button.emoji = self._pause_emoji
        self.next_page_button.emoji = self._next_emoji
        self.last_page_button.emoji = self._last_emoji
        self.numbered_page_button.emoji = self._numbered_emoji
        self.stop_button.emoji = self._stop_emoji

    def _get_embed(self) -> discord.Embed:
        """Get the current page embed with footer."""
        embed = self.embeds[self.current_page]
        embed.set_footer(text=f"{self.page_name} {self.current_page + 1}/{len(self.embeds)}")
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allow the original command invoker to use the buttons."""
        if self.ctx and interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "You cannot control this paginator.", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self) -> None:
        """Disable all buttons when the view times out."""
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass

    async def start(self, ctx: commands.Context) -> None:
        """Start the paginator.

        Parameters
        ----------
        ctx : commands.Context
            The context to send the paginator in
        """
        self.ctx = ctx

        if not self.embeds:
            raise ValueError("Empty Embeds List")

        if len(self.embeds) == 1:
            await ctx.send(embed=self.embeds[0])
            return

        self.message = await ctx.send(embed=self._get_embed(), view=self)

    @discord.ui.button(label=None, style=discord.ButtonStyle.secondary)
    async def first_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the first page"""
        if self.current_page == 0:
            return await interaction.response.defer()
        self.current_page = 0
        await interaction.response.edit_message(embed=self._get_embed())

    @discord.ui.button(label=None, style=discord.ButtonStyle.secondary)
    async def previous_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the previous page"""
        if self.current_page == 0:
            return await interaction.response.defer()
        self.current_page -= 1
        await interaction.response.edit_message(embed=self._get_embed())

    @discord.ui.button(label=None, style=discord.ButtonStyle.secondary)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Pause the paginator"""
        self.stop()
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label=None, style=discord.ButtonStyle.secondary)
    async def next_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the next page"""
        if self.current_page >= len(self.embeds) - 1:
            return await interaction.response.defer()
        self.current_page += 1
        await interaction.response.edit_message(embed=self._get_embed())

    @discord.ui.button(label=None, style=discord.ButtonStyle.secondary)
    async def last_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the last page"""
        if self.current_page == len(self.embeds) - 1:
            return await interaction.response.defer()
        self.current_page = len(self.embeds) - 1
        await interaction.response.edit_message(embed=self._get_embed())

    @discord.ui.button(label=None, style=discord.ButtonStyle.secondary)
    async def numbered_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to a custom page"""
        await interaction.response.send_message(
            f"{self.ctx.author.mention}, What {self.page_name} do you want to go to?",
            ephemeral=True,
        )

        def message_check(msg):
            return (
                msg.author.id == interaction.user.id
                and msg.channel == interaction.channel
                and msg.content.isdigit()
            )

        try:
            msg = await interaction.client.wait_for("message", check=message_check, timeout=30.0)
        except asyncio.TimeoutError:
            return
        else:
            page = int(msg.content)
            if 1 <= page <= len(self.embeds):
                self.current_page = page - 1
                await self.message.edit(embed=self._get_embed())
            try:
                await msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

    @discord.ui.button(label=None, style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Stop the paginator and delete the message"""
        self.stop()
        try:
            await self.message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

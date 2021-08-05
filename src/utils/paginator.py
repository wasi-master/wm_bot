"""File for storing the Paginator"""
import asyncio
from typing import List

import discord
from discord.ext import menus
from discord.ext.menus.views import ViewMenu

from .functions import get_custom_emoji

__all__ = ('Paginator')

class Paginator(menus.Menu):
    """Class for the Paginator"""

    def __init__(self, embeds: List[discord.Embed], page_name="Page"):
        """Initializes the paginator

        Parameters
        ----------
        embeds : List[discord.Embed]
            A list of embeds to paginate from
        page_name : str, optional
            The text to display on the footer of the embed, by default "Page"
        """
        self.embeds = embeds
        self.current_page = 0
        self.channel = None
        self.page_name = page_name
        super().__init__()

    async def send_initial_message(self, ctx, channel):
        """Send the initial message"""
        if not self.embeds:
            raise ValueError("Empty Embeds List")
        if len(self.embeds) == 1:
            await channel.send(embed=self.embeds[0])
            self.stop()
            del self
            return
        try:
            self.channel = channel
        except UnboundLocalError:
            pass
        emb = self.embeds[self.current_page].set_footer(
            text=f"{self.page_name} {self.current_page+1}/{len(self.embeds)}"
        )
        self.message = await channel.send(embed=emb)
        return self.message

    def check_skip(self):
        """Check if it should be skipped"""
        return len(self.embeds) < 2

    @menus.button(get_custom_emoji("paginator.first"), skip_if=check_skip)
    async def on_first_page(self, payload):
        """Go to the first page"""
        if self.current_page == 0:
            return
        self.current_page = 0
        await self.message.edit(
            embed=self.embeds[self.current_page].set_footer(
                text=f"{self.page_name} {self.current_page+1}/{len(self.embeds)}"
            )
        )

    @menus.button(get_custom_emoji("paginator.previous"))
    async def on_previous_page(self, payload):
        """Go to the previous page"""
        if self.current_page == 0:
            return
        self.current_page -= 1
        await self.message.edit(
            embed=self.embeds[self.current_page].set_footer(
                text=f"{self.page_name} {self.current_page+1}/{len(self.embeds)}"
            )
        )

    @menus.button(get_custom_emoji("paginator.pause"))
    async def on_pause(self, payload):
        """Pause the paginator"""
        self.stop()
        await self.message.edit(view=None)

    @menus.button(get_custom_emoji("paginator.next"))
    async def on_next_page(self, payload):
        """Go to the next page"""
        if self.current_page == len(self.embeds):
            return
        self.current_page += 1
        await self.message.edit(
            embed=self.embeds[self.current_page].set_footer(
                text=f"{self.page_name} {self.current_page+1}/{len(self.embeds)}"
            )
        )

    @menus.button(get_custom_emoji("paginator.last"), skip_if=check_skip)
    async def on_last_page(self, payload):
        """Go to the last page"""
        if self.current_page == len(self.embeds) - 1:
            return
        self.current_page = len(self.embeds) - 1
        await self.message.edit(
            embed=self.embeds[self.current_page].set_footer(
                text=f"{self.page_name} {self.current_page+1}/{len(self.embeds)}"
            )
        )

    @menus.button(get_custom_emoji("paginator.numbered"))
    async def numbered_page(self, payload):
        """Go to a custom page"""
        channel = self.message.channel
        to_delete = []
        to_delete.append(await channel.send(f"{self.ctx.author.mention}, What {self.page_name} do you want to go to?"))

        def message_check(msg):
            return msg.author.id == payload.user_id and channel == msg.channel and msg.content.isdigit()

        try:
            msg = await self.bot.wait_for("message", check=message_check, timeout=30.0)
        except asyncio.TimeoutError:
            to_delete.append(await channel.send("{self.ctx.author.mention}, You took too long."))
            await asyncio.sleep(5)
        else:
            page = int(msg.content)
            to_delete.append(msg)
            if page in range(0, len(self.embeds) - 1):
                self.current_page = page - 1
                await self.message.edit(
                    embed=self.embeds[self.current_page].set_footer(
                        text=f"page {self.current_page+1}/{len(self.embeds)}"
                    )
                )
            else:
                try:
                    await channel.delete_messages(to_delete)
                    return
                except discord.Forbidden:
                    pass

        try:
            await channel.delete_messages(to_delete)
        except discord.Forbidden:
            pass

    @menus.button(get_custom_emoji("paginator.stop"))
    async def on_stop(self, payload):
        """Stop the paginator and delete the message"""
        self.stop()
        await self.message.delete()

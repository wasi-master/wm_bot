import discord
from discord.ext import commands


class TTTButton(discord.ui.Button["TicTacToe"]):
    """A button class for managing tic tac toe"""
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y
        self.used = False
        self.xplayer = None
        self.oplayer = None

    async def callback(self, interaction: discord.Interaction):
        view: TTT = self.view
        if self.used:
            return
        valid = view.check_if_valid(self, interaction)
        if not valid:
            return
        self.used = True
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = "X"
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            if view.oplayer is not None:
                player = view.oplayer.mention
            else:
                player = "O"
            content = f"It is now {player}'s turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = "O"
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            if view.xplayer is not None:
                player = view.xplayer.mention
            else:
                player = "X"
            content = f"It is now {player}'s turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f"{view.xplayer.mention} won!"
            elif winner == view.O:
                content = f"{view.oplayer.mention} won!"
            else:
                content = "It's a tie!"

            for child in view.children:
                assert isinstance(child, discord.ui.Button)  # just to shut up the linter
                child.disabled = True

            view.stop()
        self.used = False

        await interaction.response.edit_message(content=content, view=view)


class TTT(discord.ui.View):
    """A view class for managing tic tac toe"""
    X = -1
    O = 1
    Tie = 2

    def __init__(self, xplayer, oplayer):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TTTButton(x, y))
        self.xplayer, self.oplayer = xplayer, oplayer

    def check_if_valid(self, button, interaction):
        author = interaction.user
        if self.current_player == self.X:
            if self.xplayer is None:
                self.xplayer = author
            if author != self.xplayer:
                return False
        else:
            if self.oplayer is None:
                if author == self.xplayer:
                    return False
                self.oplayer = author
            if author != self.oplayer:
                return False
        return True

    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None


class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ttt"])
    async def tictactoe(
        self,
        ctx: commands.Context,
        player1: discord.Member = None,
        player2: discord.Member = None,
    ):
        if player1 and player2:
            await ctx.send(
                f"Tic Tac Toe: {player1.mention} vs {player2.mention}," f" {player1.display_name} goes first",
                view=TTT(player1, player2),
            )
        elif player1:
            await ctx.send(
                f"Tic Tac Toe: {ctx.author.mention} vs {player1.mention}," f" {ctx.author.display_name} goes first",
                view=TTT(ctx.author, player1),
            )
        else:
            await ctx.send(
                "Tic Tac Toe: anyone vs anyone, person to click a button first goes first",
                view=TTT(None, None),
            )


def setup(bot):
    bot.add_cog(TicTacToe(bot))

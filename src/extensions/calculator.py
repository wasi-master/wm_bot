"""Calculator cog. Taken from https://github.com/pyparsing/pyparsing/blob/master/examples/fourFn.py"""
from __future__ import division

import math
import operator

import discord
from discord.ext import commands
from utils.errors import print_error

try:
    from pyparsing import (
        CaselessLiteral,
        Combine,
        Forward,
        Group,
        Literal,
        Optional,
        Word,
        ZeroOrMore,
        alphas,
        nums,
        oneOf,
    )

    HAS_PYPARSING = True
except ImportError:
    HAS_PYPARSING = False


class NumericStringParser(object):
    """
    Most of this code comes from the fourFn.py pyparsing example
    """

    def pushFirst(self, strg, loc, toks):
        self.exprStack.append(toks[0])

    def pushUMinus(self, strg, loc, toks):
        if toks and toks[0] == "-":
            self.exprStack.append("unary -")

    def __init__(self):
        """
        expop   :: '^'
        multop  :: 'x' | '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        """
        point = Literal(".")
        e = CaselessLiteral("E")
        fnumber = Combine(
            Word("+-" + nums, nums) + Optional(point + Optional(Word(nums))) + Optional(e + Word("+-" + nums, nums))
        )
        ident = Word(alphas, alphas + nums + "_$")
        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("x")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        pi = CaselessLiteral("PI")
        expr = Forward()
        atom = (
            (Optional(oneOf("- +")) + (pi | e | fnumber | ident + lpar + expr + rpar).setParseAction(self.pushFirst))
            | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
        ).setParseAction(self.pushUMinus)
        # by defining exponentiation as "atom [ ^ factor ]..." instead of
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(self.pushFirst))
        term = factor + ZeroOrMore((multop + factor).setParseAction(self.pushFirst))
        expr << term + ZeroOrMore((addop + term).setParseAction(self.pushFirst))
        # addop_term = ( addop + term ).setParseAction( self.pushFirst )
        # general_term = term + ZeroOrMore( addop_term ) | OneOrMore( addop_term)
        # expr <<  general_term
        self.bnf = expr
        # map operator symbols to corresponding arithmetic operations
        epsilon = 1e-12
        # You can add more operators here
        self.opn = {
            "+": operator.add,
            "-": operator.sub,
            "x": operator.mul,
            "**": operator.pow,
            "*": operator.mul,
            "/": operator.truediv,
            "^": operator.pow,
        }
        # functions, You can add more functions here
        self.fn = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "abs": abs,
            "trunc": int,
            "round": round,
            "floor": math.floor,
            "ceil": math.ceil,
        }

    def evaluateStack(self, s):
        op = s.pop()
        if op == "unary -":
            return -self.evaluateStack(s)
        if op in "+-x/^":
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            return self.opn[op](op1, op2)
        elif op == "PI":
            return math.pi  # 3.1415926535
        elif op == "E":
            return math.e  # 2.718281828
        elif op in self.fn:
            return self.fn[op](self.evaluateStack(s))
        elif op[0].isalpha():
            return 0
        else:
            return float(op)

    def eval(self, num_string, parseAll=True):
        self.exprStack = []
        results = self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack(self.exprStack[:])
        return val


class Calculator(commands.Cog):
    """Calculator calculates stuff (math)"""

    # Init with the bot reference, and a reference to the settings var
    def __init__(self, bot):
        self.bot = bot
        self.nsp = NumericStringParser()

    @commands.command(
        aliases=["math", "calculator", "calculate"],
        extras={"image": "https://i.imgur.com/P6PbUDi.png"},
    )
    async def calc(self, ctx, *, formula):
        """Evaluate math expressions."""
        try:
            answer = self.nsp.eval(formula)
        except Exception as e:
            return await ctx.send(f"Could not parse formula. {e}")

        if int(answer) == answer:
            # Check if it's a whole number and cast to int if so
            answer = int(answer)

        # Send answer
        await ctx.send(f"{formula} = {answer}")


def setup(bot):
    """Adds the cog to the bot"""
    if HAS_PYPARSING:
        bot.add_cog(Calculator(bot))
    else:
        print_error(
            "You don't have [yellow]pyparsing[/] installed. please install all "
            "the required packages by using [gray]`pip install -r requirements.txt`[/]"
        )

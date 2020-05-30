import random

import discord
from discord.ext import commands


class MiscCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def add(self, ctx, left: int, right: int):
        """Adds two numbers together."""
        await ctx.send(left + right)

    @commands.command()
    async def roll(self, ctx, *message: str):
        """Rolls a dice in NdN format, can process multiple commands separated by a space"""

        roll_limit = 100
        dice_side_limit = 10000

        grand_total = 0
        message_list = []
        for command in message:
            try:
                rolls, limit = map(int, command.lower().split('d'))
            except ValueError:
                await ctx.send('Format must be NdN!')
                return

            if rolls > roll_limit:
                await ctx.send('Rolls exceed limit')
                return
            if limit > dice_side_limit:
                await ctx.send('Dice size exceeds limit')
                return

            results = [random.randint(1, limit) for r in range(rolls)]
            roll_sum = sum(results)
            grand_total += roll_sum

            message = f'{rolls}D{limit}: {results} = {sum(results)}'
            message_list.append(message)

        if len(message_list) == 1:
            await ctx.send(message_list[0])
        else:
            message = '\n'.join(message_list)
            message += f'\nTotal = {grand_total}'
            await ctx.send(message)

    @commands.command(description='For when you wanna settle the score some other way')
    async def choose(self, ctx, *choices: str):
        """Chooses between multiple choices."""
        await ctx.send(random.choice(choices))

    @commands.command()
    async def repeat(self, ctx, times: int, content='repeating...'):
        """Repeats a message multiple times."""
        for i in range(times):
            await ctx.send(content)

    @commands.command()
    async def joined(self, ctx, member: discord.Member):
        """Says when a member joined."""
        await ctx.send('{0.name} joined in {0.joined_at}'.format(member))

    @commands.group()
    async def cool(self, ctx):
        """Says if a user is cool.
        In reality this just checks if a subcommand is being invoked.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('No, {0.subcommand_passed} is not cool'.format(ctx))

    @cool.command(name='bot')
    async def _bot(self, ctx):
        """Is the bot cool?"""
        await ctx.send('Yes, the bot is cool.')

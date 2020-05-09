import time

import discord
from discord.ext import commands

# Internal
from cogs.greetings import Greetings
from cogs.events import Events
from cogs.misc_commands import MiscCommands

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='!', description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

# Add cogs
bot.add_cog(Greetings(bot))
bot.add_cog(Events(bot))
bot.add_cog(MiscCommands(bot))


@bot.command()
async def server(ctx):
    await ctx.send(ctx.guild.name)


@bot.command()
async def create_channel(ctx):
    channel = await ctx.guild.create_text_channel('test')
    await channel.send('Hello!')


with open('token.txt') as file:
    token = file.read()
bot.run(token)

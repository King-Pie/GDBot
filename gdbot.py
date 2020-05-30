import time

import discord
from discord.ext import commands

# Internal
from cogs.greetings import Greetings
from cogs.events import Events
from cogs.misc_commands import MiscCommands


description = '''This is a bot created for the Generally Dangerous community. 
You can find my code at https://github.com/King-Pie/GDBot'''

bot = commands.Bot(command_prefix='!', description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    # Add playing status
    game = discord.Game("!help for commands")
    await bot.change_presence(activity=game)

# Add cogs
bot.add_cog(Greetings(bot))
bot.add_cog(Events(bot))
bot.add_cog(MiscCommands(bot))


# @bot.command()
# async def create_channel(ctx):
#     channel = await ctx.guild.create_text_channel('test')
#     await channel.send('Hello!')


with open('token.txt') as file:
    token = file.read()
bot.run(token)

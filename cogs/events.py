import datetime

import discord
from discord.ext import commands, tasks
import pendulum


class ScheduledEvent:
    def __init__(self):
        pass


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_list = []

        self.check_events.start()

    @commands.command()
    async def event(self, ctx, date, time, name):
        print(date, name, time)
        self.event_list.append(f'{name} {time}')

    @tasks.loop(seconds=10.0)
    async def check_events(self):
        print('Checking events...')
        print(self.event_list)

    @check_events.before_loop
    async def before_check_events(self):
        await self.bot.wait_until_ready()

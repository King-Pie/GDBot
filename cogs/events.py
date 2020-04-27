import datetime

import discord
from discord.ext import commands, tasks
import pendulum


class ScheduledEvent:
    def __init__(self, name: str, day: str, time: str):
        self.name = name
        self.day = day.lower().capitalize()
        self.time = time

        self.timezone = pendulum.timezone('Europe/London')
        self.datetime = pendulum.from_format(f'{self.day} {self.time}', 'ddd HH:mm', tz=self.timezone)

        self.has_triggered = False

    def is_past(self):
        return self.datetime.is_past()

    def trigger(self):
        print('Event triggered!')
        self.has_triggered = True


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_list = []

        self.check_events.start()

    @commands.command()
    async def event(self, ctx, name, day, time, timezone='GMT'):

        event = ScheduledEvent(name, day, time)
        self.event_list.append(event)

        title = f'**{name}**'
        embed = discord.Embed(title=title, colour=0x0080c0)
        embed.add_field(name=f"**Date**", value=f"{event.datetime.to_date_string()}", inline=True)
        embed.add_field(name=f"**Day**", value=f"{event.datetime.format('dddd')}", inline=True)
        embed.add_field(name=f"**Time**", value=f"{event.datetime.format('HH:mm')} {event.timezone.name}\n"
                                                f"{event.datetime.in_timezone('Europe/Stockholm').format('HH:mm')} "
                                                f"{'Europe/Stockholm'}",
                        inline=True)
        embed.add_field(name="What now?", value="React below if you can attend! "
                                                "You'll be reminded when the event starts")
        embed.set_footer(text="Tip: You might be able to edit this event eventually")

        await ctx.send(embed=embed)

    @tasks.loop(seconds=10.0)
    async def check_events(self):
        print('Checking events...')
        for e in self.event_list:
            if e.is_past():
                e.trigger()

    @check_events.before_loop
    async def before_check_events(self):
        await self.bot.wait_until_ready()

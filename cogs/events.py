import json
import pathlib

import discord
from discord.ext import commands, tasks
import pendulum


class ScheduledEvent:
    def __init__(self, bot, event_name: str, day: str, time: str):

        self.bot = bot
        self.event_name = event_name
        self.day = day.lower().capitalize()
        self.time = time
        self.timezone = 'Europe/London'
        self.date = self.get_initial_date()

        self.has_triggered = False

        # Announcement message IDs
        self.host_id = None
        self.announce_channel_id = None
        self.announce_message_id = None

    def to_dict(self):
        return {
            'event_name': self.event_name,
            'day': self.day,
            'time': self.time,
            'timezone': self.timezone,
            'date': self.date,
            'has_triggered': self.has_triggered,
            'host_id': self.host_id,
            'announce_channel_id': self.announce_channel_id,
            'announce_message_id': self.announce_message_id
        }

    def get_initial_date(self):
        # Gets the nearest date which matches the day string given
        datetime = pendulum.from_format(f'{self.day} {self.time}', 'ddd HH:mm', tz=pendulum.timezone(self.timezone))
        # If the time is in the past then add a week
        if datetime.is_past():
            datetime = datetime.add(weeks=1)
        return datetime.to_date_string()

    def get_datetime(self):

        datetime = pendulum.from_format(f'{self.date} {self.time}',
                                        'YYYY-MM-DD HH:mm', tz=pendulum.timezone(self.timezone))
        return datetime

    async def send_announcement_message(self, ctx):

        datetime = self.get_datetime()

        # Construct embed
        host = ctx.author
        title = f'**{self.event_name}**'
        embed = discord.Embed(title=title, colour=0x0080c0)
        embed.add_field(name="**Host**", value=f"{host.mention}", inline=False)
        embed.add_field(name=f"**Date**", value=f"{datetime.to_date_string()}", inline=True)
        embed.add_field(name=f"**Day**", value=f"{datetime.format('dddd')}", inline=True)
        embed.add_field(name=f"**Time**", value=f"{datetime.format('HH:mm')} {self.timezone}\n"
                                                f"{datetime.in_timezone('Europe/Stockholm').format('HH:mm')} "
                                                f"{'Europe/Stockholm'}",
                        inline=True)
        embed.add_field(name="What now?", value="React below if you can attend! "
                                                "You'll be reminded when the event starts", inline=False)
        embed.set_footer(text="Tip: You might be able to edit this event eventually")

        # Send embed
        event_message = await ctx.send(embed=embed)

        # Get the host, channel and message ID for the sent message - this is to check the reactions later
        self.host_id = host.id
        self.announce_channel_id = ctx.channel.id
        self.announce_message_id = event_message.id
        channel = self.bot.get_channel(self.announce_channel_id)
        msg = await channel.fetch_message(self.announce_message_id)
        await msg.add_reaction(u"\U0001F44D")

        # user = bot.get_user(self.host_id)
        # await ctx.send(f'Okay {user.mention}')

    async def send_reminder_message(self):

        # Get users who reacted to original message
        announcement_channel = self.bot.get_channel(self.announce_channel_id)
        announcement_message = await announcement_channel.fetch_message(self.announce_message_id)

        user_list = []
        for reaction in announcement_message.reactions:
            if reaction.me:
                user_list = await reaction.users().flatten()

        user_mentions = [user.mention for user in user_list if not user.bot]
        mention_string = ' '.join(user_mentions)
        host = self.bot.get_user(self.host_id)

        await announcement_channel.send(f"Hey {mention_string}. {self.event_name} hosted by {host.mention} "
                                        f"is starting now!")

    def should_trigger(self):

        datetime = self.get_datetime()

        if datetime.is_past() and not self.has_triggered:
            return True
        else:
            return False

    async def trigger(self):
        print(f'{self.event_name} Event triggered!')
        self.has_triggered = True
        await self.send_reminder_message()


def event_from_json(bot, json_string):

    data = json.loads(json_string)

    event = ScheduledEvent(
        bot=bot,
        event_name=data['event_name'],
        day=data['day'],
        time=data['time'])

    event.timezone = data['timezone']
    event.date = data['date']

    event.has_triggered = data['has_triggered']

    # Announcement message IDs
    event.host_id = data['host_id']
    event.announce_channel_id = data['announce_channel_id']
    event.announce_message_id = data['announce_message_id']

    return event


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.event_file_path = pathlib.Path('cogs/events.json')
        # Checks if event file path exists, creates it if not
        self.initialise_event_data_file()
        self.event_list = self.load_event_list_from_json()

        self.event_channel = None
        self.check_events.start()

    def save_event_list_to_json(self):

        json_event_list = [json.dumps(event.to_dict(), indent=4) for event in self.event_list]
        with open(self.event_file_path, 'w') as f:
            json.dump(json_event_list, f, indent=4)

    def load_event_list_from_json(self):

        with open(self.event_file_path, 'r') as f:
            json_event_list = json.load(f)

        event_list = []
        for json_event in json_event_list:
            event_list.append(event_from_json(self.bot, json_event))

        return event_list

    def initialise_event_data_file(self):

        if not self.event_file_path.exists():
            with open(self.event_file_path, 'w') as f:
                json.dump([], f)

    @commands.command()
    async def set_event_channel(self, ctx):

        self.event_channel = ctx.channel

        await ctx.send(f"Event channel set!")

    @commands.command()
    async def event(self, ctx, name, day, time, timezone='GMT'):

        event = ScheduledEvent(self.bot, name, day, time)
        await event.send_announcement_message(ctx)

        self.event_list.append(event)
        self.save_event_list_to_json()

        self.load_event_list_from_json()

    @tasks.loop(seconds=10.0)
    async def check_events(self):
        print('Checking events...')
        for e in self.event_list:
            if e.has_triggered:
                self.event_list.remove(e)
                self.save_event_list_to_json()

            if e.should_trigger():
                await e.trigger()

    @check_events.before_loop
    async def before_check_events(self):
        await self.bot.wait_until_ready()

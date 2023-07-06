"""Command line tool to harvest messages from every channel in a guild and add them to the Qdrant vector store"""
from dotenv import load_dotenv
import discord
from discord.ext import commands
from os import getenv
from vectors import Vectinator
from datetime import datetime
from typing import TypedDict, Mapping
from os.path import isfile
import pickle

load_dotenv()
TOKEN = getenv('TOKEN')
GUILD_ID = getenv('GUILD_ID')

if TOKEN is None:
    print("TOKEN is not set in .env file.")
    exit(1)

if GUILD_ID is None:
    print("GUILD_ID is not set in .env file.")
    exit(1)


vectinator = Vectinator()


class SimpleChannel(TypedDict):
    name: str
    highwater: datetime | None


# We will use this channel map to keep track of which channels we have already harvested, and to what point in time
# We will save this to disk so we can resume harvesting if the process is interrupted
channelmap: dict[int, SimpleChannel] = {}
if isfile('channels.pickle'):
    with open('channels.pickle', 'rb') as f:
        channelmap = pickle.load(f)


class HarvesterClient(discord.Client):
    async def on_ready(self) -> None:
        print('Logged on as', self.user)
        this_guild: discord.Guild = discord.utils.get(self.guilds, id=int(GUILD_ID))  # type: ignore
        print('self.guilds', self.guilds)
        if this_guild is None:
            print(f"Guild with id {GUILD_ID} not found")
            return
        # populate our channel map with the current channels
        for channel in this_guild.text_channels:
            if isinstance(channel.id, int) and channel.id not in channelmap:
                channelmap[channel.id] = SimpleChannel(name=channel.name, highwater=None)
        # harvest messages from all channels
        try:
            for count, channel in enumerate(this_guild.text_channels):
                print(f"Reading {channel.name} in {this_guild.name} ({count+1}/{len(this_guild.text_channels)})")
                try:  # try-except block in case bot doesn't have message history permissions
                    # iterate through the messages in the channel after the highwater mark for this channel
                    async for msg in channel.history(limit=None, after=channelmap[channel.id]['highwater']):
                        # update the highwater mark for this channel
                        hw = channelmap[channel.id]['highwater']  # Pylance is weird, it will not infer if you check on a dictionary value
                        if hw is None or msg.created_at > hw:
                            channelmap[channel.id]['highwater'] = msg.created_at
                        # save in our database, this is an upsert operation but we shouldn't be duplicating heaps
                        # with the date highwater checks.
                        vectinator.save_message(msg)
                except discord.errors.Forbidden:
                    print(f"No permission to read {channel.name} in {this_guild.name}")
            print("Harvest done!")
        except:
            # Some shit, any shit, went wrong so save what we did so far
            print("Error reading channels")
            # save the channel map
            with open('channels.pickle', 'wb') as f:
                pickle.dump(channelmap, f)
            print("Channel map saved")


if __name__ == "__main__":
    # Enable privileged Gateway Intents
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False
    intents.messages = True
    intents.message_content = True
    intents.guilds = True
    # Start the harvester client
    client = HarvesterClient(intents=intents)
    client.run(TOKEN)

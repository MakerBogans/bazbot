"""Command line tool to harvest messages from every channel in a guild and add them to the Qdrant vector store"""
from dotenv import load_dotenv
import discord
from discord.ext import commands
from os import getenv
from vectors import Vectinator

load_dotenv()
TOKEN = getenv('TOKEN')
GUILD_ID = getenv('GUILD_ID')

if TOKEN is None:
    print("TOKEN is not set in .env file.")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix='!')
vectinator = Vectinator()


class HarvesterClient(discord.Client):
    async def on_ready(self) -> None:
        print('Logged on as', self.user)
        this_guild = discord.utils.get(self.guilds, id=int(GUILD_ID))
        print('self.guilds', self.guilds)
        if this_guild is None:
            print(f"Guild with id {GUILD_ID} not found")
            return
        for channel in this_guild.text_channels:
            print(f"Reading {channel.name} in {this_guild.name}")
            try:  # try-except block in case bot doesn't have message history permissions
                async for msg in channel.history(limit=None):
                    self.save_message(msg)
            except discord.errors.Forbidden:
                print(f"No permission to read {channel.name} in {this_guild.name}")
        print("Done")

    def save_message(self, message: discord.Message) -> None:
        print(f"Saving message {message.content}")
        #vectinator.save_message(message)

# Enable privileged Gateway Intents
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
intents.guilds = True

# Start the bot
client = HarvesterClient(intents=intents)
client.run(TOKEN)


if __name__ == "__main__":
    # Blocking command that starts the event loop
    bot.run(TOKEN)

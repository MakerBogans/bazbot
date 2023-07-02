# Bot permissions integer 84992
# https://discord.com/api/oauth2/authorize?client_id=1100283582070673479&permissions=19456&scope=bot

from dotenv import load_dotenv
import discord
from discord.ext import commands
from os import getenv
from vectors import Vectinator
from arq import create_pool, ArqRedis
from arq.connections import RedisSettings

load_dotenv()
TOKEN = getenv('TOKEN')
GUILD = getenv('GUILD')

if TOKEN is None:
    print("TOKEN is not set in .env file.")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix='!')
vectinator = Vectinator()
redis: ArqRedis | None = None

@bot.event
async def on_ready():
    global redis
    redis = await create_pool(RedisSettings())
    guild = discord.utils.get(bot.guilds, name=GUILD)
    if guild is not None:
        print(f'{bot.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})')

@bot.event
async def on_message(message: discord.Message):
    # Ignore messages from the bot itself. Or should we? 
    # !bot commands responses perhaps should be saved?
    if message.author == bot.user:
        return
    vectinator.save_message(message)
    # Let bot process commands in addition to the above "on_message" handling.
    await bot.process_commands(message)

@bot.command(name='baz')
async def baz(ctx: commands.Context):
    # Set typing indicator
    async with ctx.typing():
        # Make a description of the place this message occured
        channel_name = f"the {ctx.channel.name} channel" if isinstance(ctx.channel, discord.TextChannel) else "a private message"
        # Send the task to worker via arq/reddis
        assert redis is not None
        job = await redis.enqueue_job('command', ctx.author.display_name, channel_name, ctx.message.content)
        if job is None:
            await ctx.send("Job is None")
            return
        try:
            # Wait for the response from the worker
            response = await job.result(timeout=10)
            if response is not None:
                # Send the response back to the channel
                await ctx.send(response)
        except TimeoutError:
            await ctx.send("Baz is taking too long to respond, please try again later. Or get fucked.")
            return


if __name__ == "__main__":
    # Blocking command that starts the event loop
    bot.run(TOKEN)

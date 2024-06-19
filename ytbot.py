from pytube_utils import *
import discord
import os
import random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
PREFIX = os.getenv('BOT_PREFIX', '!')

intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}, with {PREFIX} as prefix')

@bot.command(aliases=['h'])
async def hello(ctx):
    greets = ['Hello!', 'Yo!', 'Greetings!', 'Hej!']
    rng = random.randrange(0, len(greets)-1, 1)
    await ctx.send(greets[rng])

@bot.command(aliases=['j'])
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You are not in a voice channel")

@bot.command(aliases=['p'])
async def play(ctx, *args):
    if ctx.voice_client:

        url = ' '.join(args)
        voice_client = ctx.voice_client

        await ctx.send(f'looking for `{url}`...')
        audio_file = getAudioFile(url)
        if audio_file is None:
            audio_file = fastSearch(url)
            if audio_file is None:
                await ctx.send(f"Could not find {url}")
            else:
                await ctx.send(f'Downloading: `{url}`')
                voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=audio_file), after=lambda e: os.remove(audio_file)) # Play the audio using FFmpeg
        else:
            await ctx.send(f'Downloading: `{url}`')
            voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=audio_file), after=lambda e: os.remove(audio_file)) # Play the audio using FFmpeg

    else:
        await ctx.send(f"I'm not in a voice channel. Use `{PREFIX}join` to bring me into one.")

def main():
    if TOKEN is None:
        return ("""no token provided. Please create a .env file containing the token. 
                `for more information view the README.md
                """)
    
    try: bot.run(TOKEN)
    except discord.PrivilegedIntentsRequired as error:
        return error

if __name__ == "__main__":
    main()
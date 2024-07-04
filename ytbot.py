from ytdlp_utils import *

import os
import datetime
#import asyncio
import random
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
PREFIX = os.getenv('BOT_PREFIX', '!')

intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

last_activity_date = datetime.datetime.now()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}, with {PREFIX} as prefix')
    check_inactivity.start()

@bot.command(aliases=['h'])
async def hello(ctx):
    greets = ['Hello', 'Yo', 'Greetings', 'Hej']
    rng = random.randrange(0, len(greets)-1, 1)
    await ctx.send(greets[rng])

@bot.command(aliases=['j'])
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        reset_timer()
    else:
        await ctx.send("You are not in a voice channel")

@bot.command(aliases=["l", "begone"])
async def leave(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
    else:
        await ctx.send("Bot is not connected to any voice channel.")

@bot.command(aliases=['s'])
async def skip(ctx):
    voice_client = ctx.guild.voice_client
    voice_client.stop()
    reset_timer()


@bot.command(aliases=['p'])
async def play(ctx, *args):

    if ctx.author.voice:
        if not ctx.voice_client:
            channel = ctx.author.voice.channel
            await channel.connect()
        
        if ctx.voice_client:
            reset_timer()

            url = ' '.join(args)
            voice_client = ctx.voice_client
            server_id = ctx.guild.id


            await ctx.send(f'looking for `{url}`...')
            info_dict = downloadAudioFile(url, server_id)
            filepath = f'./audio_files/{server_id}/{info_dict["id"]}.{info_dict["ext"]}'
            if info_dict is None:
                await ctx.send(f"Could not find {url}")
            else:
                # await ctx.send(f'Downloading: `{url}`')
                voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=filepath), after=lambda e: os.remove(filepath))
                await ctx.send(f'Now playing: `{info_dict["title"]}`')
                
    else:
        await ctx.send("You are not in a voice channel")

   

def reset_timer():
    global last_activity_date
    last_activity_date = datetime.datetime.now()

@tasks.loop(minutes=1)
async def check_inactivity():
    global last_activity_date
    if bot.voice_clients:
        for vc in bot.voice_clients:
            if not vc.is_playing() and (datetime.datetime.now() - last_activity_date).total_seconds() > 600:
                await vc.disconnect()
                print("Disconnected due to inactivity")

def main():
    if TOKEN is None:
        return ("No token provided. Please create an \".env\" file in the style of \".env_test.\"")
    
    try: bot.run(TOKEN)
    except discord.PrivilegedIntentsRequired as error:
        return error

if __name__ == "__main__":
    main()
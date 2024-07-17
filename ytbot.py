from ytdlp_utils import *

import os
import shutil 
import datetime
import asyncio
import random
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
PREFIX = os.getenv('BOT_PREFIX', '!')
TIMEOUT_MIN = 10

intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

last_activity_date = datetime.datetime.now()
server_queues = {}

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
        server_queues[ctx.guild.id] = []
    else:
        await ctx.send("You are not in a voice channel")

@bot.command(aliases=["l", "begone"])
async def leave(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
    else:
        await ctx.send("Bot is not connected to any voice channel.")

@bot.command(aliases=['s']) # NEEDS FIXING FOR THE QUEUE
async def skip(ctx):
    voice_client = ctx.guild.voice_client
    
    voice_client.stop()
    reset_timer()


@bot.command(aliases=['p'])
async def play(ctx, *args):

    if ctx.author.voice: # is the chatter in a voice channel? # EXTRACT THIS TO ANOTHER CHECK FUNCTION!
        server_id = ctx.guild.id
        if not ctx.voice_client: # is the bot in the same channel?
            channel = ctx.author.voice.channel
            await channel.connect()
            server_queues[server_id] = []
        
        if ctx.voice_client:
            reset_timer()

            url = ' '.join(args)
            voice_client = ctx.voice_client

            if(url.startswith("https://www.youtu")):
                title = getTitle(url)
                await ctx.send(f'looking for `{title}`...')
                
            else:
                await ctx.send(f'searching for `{url}`...')
            
            info_dict = downloadAudioFile(url, server_id)

            if info_dict is None:
                await ctx.send(f"Could not find {url}")
            else:

                filepath = f'./audio_files/{server_id}/{info_dict["id"]}.{info_dict["ext"]}'
                server_queues[server_id].append(filepath)

                if not voice_client.is_playing() and len(server_queues[server_id]) == 1:
                    await play_next(voice_client, server_id)
                
    else:
        await ctx.send("You are not in a voice channel")

async def play_next(voice_client, server_id):
    filepath = server_queues[server_id].pop()
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable="ffmpeg", source=filepath), volume=0.2)
    voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(voice_client, server_id), bot.loop))

    reset_timer()
   

def reset_timer():
    global last_activity_date
    last_activity_date = datetime.datetime.now()

@bot.event
async def on_voice_state_update(member: discord.User, before: discord.VoiceState, after: discord.VoiceState):
    if member != bot.user:
        return
    if before.channel is not None and after.channel is None: # remove the downloaded files whenever the bot leaves.
        server_id = before.channel.guild.id
        try: server_queues.pop(server_id)
        except: pass
        try: shutil.rmtree(f'./audio_files/{server_id}/')
        except: pass

@tasks.loop(minutes=1)
async def check_inactivity():
    global last_activity_date
    if bot.voice_clients:
        for vc in bot.voice_clients:
            if not vc.is_playing() and (datetime.datetime.now() - last_activity_date).total_seconds() > (TIMEOUT_MIN * 60):
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
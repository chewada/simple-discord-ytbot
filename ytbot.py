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

@bot.command(aliases=['s'])
async def skip(ctx, *args):
    voice_client = ctx.guild.voice_client

    try: skip_num = int(args[0])
    except:
        skip_num = 1
    server_id = ctx.guild.id
    try:
        queue = server_queues[server_id]
    except KeyError:
        await ctx.send(f'There is nothing in the queue')

    if skip_num > 1:
        if skip_num <= len(queue):
            info_dict = queue.pop(skip_num-1)[1]
            await ctx.send(f'Skipped: `{info_dict["title"]}`')
        else:
            await ctx.send(f'There is no song in the queue with index: {skip_num}')
    else:
        voice_client.stop() # skip current song
    reset_timer()

@bot.command(aliases=['q'])
async def queue(ctx):
    server_id = ctx.guild.id
    current_queue = "Songs currently in the queue:"
    i = 1
    try:
        queue = server_queues[server_id]
    except KeyError:
        await ctx.send(f'There is nothing in the queue')

    for song_info in queue:
        info_dict = song_info[1]
        current_queue += f'\n`{i}. {info_dict["title"]}: {datetime.timedelta(seconds=info_dict["duration"])}`'
        i += 1

    await ctx.send(current_queue)

@bot.command(aliases=['p'])
async def play(ctx, *args):

    if ctx.author.voice: # is the chatter in a voice channel? # EXTRACT THIS TO ANOTHER CHECK FUNCTION!
        server_id = ctx.guild.id
        if not ctx.voice_client: # is the bot in the same channel? Otherwise join the channel
            channel = ctx.author.voice.channel
            await channel.connect()
            server_queues[server_id] = []
        
        if ctx.voice_client:
            reset_timer()

            url = ' '.join(args)
            voice_client = ctx.voice_client
            
            info_dict = downloadAudioFile(url, server_id)

            if info_dict is None:
                await ctx.send(f"Could not find {url}")
            else:
                await ctx.send(f'Found: `{info_dict["title"]}`')

                filepath = f'./audio_files/{server_id}/{info_dict["id"]}.{info_dict["ext"]}'
                server_queues[server_id].append((filepath, info_dict))

                if not voice_client.is_playing() and len(server_queues[server_id]) == 1:
                    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable="ffmpeg", source=filepath), volume=0.2)
                    voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(voice_client, server_id), bot.loop))
                
    else:
        await ctx.send("You are not in a voice channel")

@bot.command(aliases=['pl'])
async def playlist(ctx, *args):

    if ctx.author.voice: 
        server_id = ctx.guild.id
        if not ctx.voice_client: # is the bot in the same channel? Otherwise join the channel
            channel = ctx.author.voice.channel
            await channel.connect()
            server_queues[server_id] = []
        
        if ctx.voice_client:
            reset_timer()

            voice_client = ctx.voice_client
            url = args[0]
            random = False
            try:
                random = args[1] == "random"
                if random:
                    await ctx.send(f"The playlist will be randomized :)")
            except IndexError:
                pass
            
            playlist_dict = downloadPlaylist(url, server_id, random)
            if playlist_dict is None:
                await ctx.send(f"Could not find the playlist")
            else:
                await ctx.send(f'Found a playlist: `{playlist_dict["title"]}`')

                for info_dict in playlist_dict['entries']:

                    filepath = f'./audio_files/{server_id}/{info_dict["id"]}.{info_dict["ext"]}'
                    server_queues[server_id].append((filepath, info_dict))

                    if not voice_client.is_playing() and len(server_queues[server_id]) == 1:
                        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable="ffmpeg", source=filepath), volume=0.2)
                        voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(voice_client, server_id), bot.loop))
    else:
        await ctx.send("You are not in a voice channel")


async def play_next(voice_client, server_id):
    server_queues[server_id].pop(0) # remove the previous song data
    if len(server_queues[server_id]) != 0:
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable="ffmpeg", source=server_queues[server_id][0][0]), volume=0.2)
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
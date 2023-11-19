"""
this works and can play music, needs good upload speed of at least 25
to do:
- implement queue's
- implement buttons
- implement interface to be displayed in discord
"""

import discord, asyncio, yt_dlp
# import pafy, urllib.request, json, urllib, os
# from discord.ext import commands
# from discord_buttons_plugin import *
# from pytube import Playlist
from collections import deque

with open('bot_keys', 'r') as f:
    bot_token = f.read().strip()

# lofi_bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())
# lofi_bot.add_cog(help_cog(lofi_bot))

client = discord.Client(command_prefix='$', intents=discord.Intents.all())
# bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())
key = bot_token
voice_clients = {}
yt_dl_opts = {"format": 'bestaudio/best'}
ytdl = yt_dlp.YoutubeDL(yt_dl_opts)
song_queues = {}
song_queue_name = deque()
voice_status = 'not connected'

ffmpeg_options = {'options': '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 15'}


# runtime configuration
@client.event
async def on_ready():
    print(f"Bot is ready")
    await client.change_presence(activity=discord.Game(name='цигу мигу чакарака'))


# Receiver
@client.event
async def on_message(msg):
    global voice_status
    if msg.content.startswith('$play'):

        # create voice client connection
        if voice_status != 'connected':
            try:
                voice_client = await msg.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client
                voice_status = 'connected'
            except Exception as err:
                await msg.channel.send('Влез в music канала.')
                voice_status = 'not connected'
                print(err)

        # play song
        try:
            url = msg.content.split()[1]
            bot_chat = None
            if url == 'skakauec':
                url = 'https://www.youtube.com/watch?v=pq3C-UE6RE0'
                bot_chat = 'Пущам СКАКАУЕЦ!'
            elif url == 'sans':
                url = 'https://www.youtube.com/watch?v=0FCvzsVlXpQ'
                bot_chat = 'https://tenor.com/view/funny-dance-undertale-sans-gif-26048955'
            elif url == 'ignf':
                url = 'https://www.youtube.com/watch?v=yLnd3AYEd2k'
                bot_chat = 'https://tenor.com/view/actorindie-worlds-smallest-violin-aww-violin-gif-13297153'
            # elif 'http' not in url:
            #     async def search_and_play(query):
            #         ydl_opts = {
            #             'query': query,
            #             'max_results': 1,
            #             'format': 'bestaudio/best',
            #         }
            #         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            #             results = ydl.extract_info(query, download=False)
            #
            #             if 'entries' in results and results['entries']:
            #                 entry = results['entries'][0]
            #                 url = entry['url']
            #                 return url
            #     await search_and_play(url)

            # checking if guild has a queue
            if msg.guild.id not in song_queues:
                song_queues[msg.guild.id] = []

            # notify in chat that song is added
            if get_video_name(url) != 'Video title not available' and \
                    get_video_name(url) != 'Error retrieving video title':
                await msg.channel.send(f"Добавена песен в плейлиста: {get_video_name(url)}")
                song_queues[msg.guild.id].append(url)
                song_queue_name.append(get_video_name(url))
            else:
                await msg.channel.send('Пробуем при намирането на таз песен.')

            # if only 1 song, play it
            if len(song_queues[msg.guild.id]) > 1:
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

                song = data['url']
                player = discord.FFmpegPCMAudio(song, **ffmpeg_options, executable="/usr/bin/ffmpeg")

                # voice_client.play(player)
                voice_clients[msg.guild.id].play(player)

                if bot_chat:
                    await msg.channel.send(bot_chat)

                await client.change_presence(activity=discord.Game(name=get_video_name(url)))

                # song_queues[msg.guild.id].popleft()
                # song_queue_name.popleft()

        except yt_dlp.DownloadError:
            await msg.channel.send(f"Нема такова '{str(url)}'")
            await voice_clients[msg.guild.id].disconnect()
            voice_status = 'not connected'
        except Exception as err:
            await msg.channel.send("ГРЕДА")
            await voice_clients[msg.guild.id].disconnect()
            voice_status = 'not connected'
            print(err)

    if msg.content.startswith("$pause"):
        try:
            voice_clients[msg.guild.id].pause()
        except Exception as err:
            print(err)

    if msg.content.startswith("$resume"):
        try:
            voice_clients[msg.guild.id].resume()
        except Exception as err:
            print(err)

    if msg.content.startswith("$stop"):
        try:
            voice_clients[msg.guild.id].stop()
            await voice_clients[msg.guild.id].disconnect()
            voice_status = 'not connected'
            del song_queues[msg.guild.id]
            song_queue_name.clear()
        except Exception as err:
            print(err)

    if msg.content.startswith("$queue"):
        if msg.guild.id in song_queues and song_queue_name:
            queue_list = '\n'.join(song_queue_name)
            await msg.channel.send(f"Плейлист:\n{queue_list}")
        else:
            await msg.channel.send('Нема плейлист')


def get_video_name(youtube_url):
    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            result = ydl.extract_info(youtube_url, download=False)
            if 'title' in result:
                return result['title']
            else:
                return "Video title not available"
    except yt_dlp.DownloadError as e:
        print(f"Error: {e}")
        return "Error retrieving video title"


client.run(key)

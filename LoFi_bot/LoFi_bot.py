"""
this works and can play music, needs good upload speed of at least 25
to do:
- implement queue's
- implement buttons
- implement interface to be displayed in discord
"""

import discord, asyncio, yt_dlp, pafy, urllib.request, json, urllib, os
from discord.ext import commands
from discord_buttons_plugin import *
from pytube import Playlist

# lofi_bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())
# lofi_bot.add_cog(help_cog(lofi_bot))

client = discord.Client(command_prefix='$', intents=discord.Intents.all())
key = 'discord bot key'

voice_clients = {}
yt_dl_opts = {"format": 'bestaudio/best'}
ytdl = yt_dlp.YoutubeDL(yt_dl_opts)

ffmpeg_options = {'options': '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}


# runtime configuration
@client.event
async def on_ready():
    print(f"Bot is ready")
    await client.change_presence(activity=discord.Game(name='цигу мигу чакарака'))


# Receiver
@client.event
async def on_message(msg):
    if msg.content.startswith('$play'):

        # create voice client connection
        try:
            voice_client = await msg.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except Exception as err:
            print(err)

        try:
            url = msg.content.split()[1]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegPCMAudio(song, **ffmpeg_options, executable="/usr/bin/ffmpeg")

            # voice_client.play(player)
            voice_clients[msg.guild.id].play(player)

        except Exception as err:
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
        except Exception as err:
            print(err)

client.run(key)

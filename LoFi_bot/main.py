import discord
import asyncio
import yt_dlp
from discord.ext import commands
from discord_buttons_plugin import ButtonsClient, Button

client = commands.Bot(command_prefix='$', intents=discord.Intents.all())
buttons = ButtonsClient(client)

key = 'discord bot key'

voice_clients = {}
yt_dl_opts = {"format": '251'}
ytdl = yt_dlp.YoutubeDL(yt_dl_opts)

ffmpeg_options = {'options': '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}

# Register button callbacks
@buttons.click
async def on_button_click(interaction):
    if interaction.custom_id == "play":
        await play(interaction)
    elif interaction.custom_id == "pause":
        await pause(interaction)
    elif interaction.custom_id == "resume":
        await resume(interaction)
    elif interaction.custom_id == "stop":
        await stop(interaction)
    elif interaction.custom_id == "next":
        await next_song(interaction)

async def play(msg):
    try:
        voice_client = await msg.author.voice.channel.connect()
        voice_clients[voice_client.guild.id] = voice_client
    except Exception as err:
        print(err)

    try:
        url = msg.message.content.split()[1]

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        song = data['url']
        player = discord.FFmpegPCMAudio(song, **ffmpeg_options, executable="/usr/bin/ffmpeg")

        voice_clients[msg.guild.id].play(player)

    except Exception as err:
        print(err)

async def pause(msg):
    try:
        voice_clients[msg.guild.id].pause()
    except Exception as err:
        print(err)

async def resume(msg):
    try:
        voice_clients[msg.guild.id].resume()
    except Exception as err:
        print(err)

async def stop(msg):
    try:
        voice_clients[msg.guild.id].stop()
        await voice_clients[msg.guild.id].disconnect()
    except Exception as err:
        print(err)

async def next_song(msg):
    # Implement your logic for playing the next song
    pass

# runtime configuration
@client.event
async def on_ready():
    print(f"Bot is ready")
    await client.change_presence(activity=discord.Game(name='цигу мигу чакарака'))

    # Send message with buttons
    await buttons.send(
        content="Click the buttons to control playback",
        channel='695632304290398288',
        components=[
            Button(style=1, label="Play", custom_id="play"),  # Style 1 corresponds to green
            Button(style=4, label="Pause", custom_id="pause"),  # Style 4 corresponds to red
            Button(style=3, label="Resume", custom_id="resume"),  # Style 3 corresponds to blue
            Button(style=2, label="Stop", custom_id="stop"),  # Style 2 corresponds to gray
            Button(style=2, label="Next", custom_id="next"),  # Style 2 corresponds to gray
        ]
    )


client.run(key)

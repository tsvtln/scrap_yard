# import discord
# import asyncio
# import yt_dlp
# from collections import deque
# import os
# import glob
# import sys
#
# class MusicBot:
#     def __init__(self, bot_token):
#         self.bot = discord.Client(command_prefix='$', intents=discord.Intents.all())
#         self.yt_dl_opts = {"format": 'bestaudio/best',
#                           "postprocessors": [{
#                               "key": "FFmpegExtractAudio",
#                               "preferredcodec": "mp3",
#                               "preferredquality": "192"
#                           }],
#                           "restrictfilenames": True,
#                           "retry_max": "auto",
#                           "noplaylist": True,
#                           "nocheckcertificate": True,
#                           "quiet": True,
#                           "no_warnings": True,
#                           "verbose": False,
#                           "allow_multiple_audio_streams": True
#                           }
#         self.ffmpeg_options = {
#             'options': '-vn -reconnect 15 -reconnect_streamed 15 -reconnect_delay_max 15'
#         }
#         self.song_queues = {}
#         self.song_queue_name = deque()
#         self.ytdl = yt_dlp.YoutubeDL(self.yt_dl_opts)
#         self.files_to_clean = []
#
#     def run(self):
#         self.bot.run(bot_token)
#
#     @staticmethod
#     def get_video_name(youtube_url):
#         try:
#             with yt_dlp.YoutubeDL({}) as ydl:
#                 result = ydl.extract_info(youtube_url, download=False)
#                 if 'title' in result:
#                     return result['title']
#                 else:
#                     return "Video title not available"
#         except yt_dlp.DownloadError as e:
#             print(f"Error: {e}")
#             return "Error retrieving video title"
#
#     @staticmethod
#     def find_video_url(search_query):
#         ydl_opts = yt_dl_opts
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             video = ydl.extract_info(f"ytsearch:{search_query}", ie_key='YoutubeSearch')['entries'][0]
#             return video['webpage_url']
#
#     class NotInVoiceChannel(Exception):
#         """A custom exception class to raise an error if user is not in a voice channel."""
#
#         def __init__(self, message="User not in voice channel."):
#             self.message = message
#             super().__init__(self.message)
#
#     @staticmethod
#     async def find_files_to_clean(bot):
#         """ collects a list of files to be cleaned"""
#         global files_to_clean
#         files_to_clean.clear()
#         pattern = os.path.join('.', '*.webm')
#         files_to_clean = glob.glob(pattern)
#
#     @staticmethod
#     async def clean_files(bot):
#         global files_to_clean
#         for file in files_to_clean:
#             os.remove(file)
#             print(f"Cleared {file} from local repo")
#
#     class SuppressYouTubeMessages:
#         """ filters out [youtube] blablabla messages """
#
#         def write(self, message):
#             if '[youtube]' not in message:
#                 sys.__stdout__.write(message)
#
#         def flush(self):
#             pass
#
#     @staticmethod
#     def set_suppress_output(suppress):
#         if suppress:
#             sys.stdout = MusicBot.SuppressYouTubeMessages()
#         else:
#             sys.stdout = sys.__stdout__
#
#     async def on_ready(self):
#         print(f"Music bot is ready")
#         await self.bot.change_presence(activity=discord.Game(name='цигу мигу чакарака'))
#
#     @staticmethod
#     async def on_message(bot, msg):
#         if msg.content.startswith('$play'):
#             if msg.guild.id not in bot.voice_clients:
#                 try:
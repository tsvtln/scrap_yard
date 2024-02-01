import discord
import asyncio
import yt_dlp
from collections import deque
import os
import glob


class MusicBot(discord.Client):
    def __init__(self, command_prefix='$', **options):
        super().__init__(command_prefix=command_prefix, **options, intents=discord.Intents.all())
        self.voice_clients = {}
        self.song_queues = {}
        self.yt_dl_opts = {
            "format": 'bestaudio/best',
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredquality": "192"
            }],
            "restrictfilenames": True,
            "retry_max": "auto",
            "noplaylist": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "verbose": False,
            'allow_multiple_audio_streams': True
        }
        self.ffmpeg_options = {
            'options': '-vn -reconnect 15 -reconnect_streamed 15 -reconnect_delay_max 15'
        }
        self.song_queue_name = deque()
        self.ytdl = yt_dlp.YoutubeDL(self.yt_dl_opts)
        self.voice_status = 'not connected'
        self.url = ''
        self.bot_chat = None
        self.files_to_clean = []
        self.bot_token = ''
        self.guild_id = {}

    @property
    def voice_clients(self):
        return self._voice_clients

    @voice_clients.setter
    def voice_clients(self, value):
        self._voice_clients = value

    @property
    def bot_token(self):
        return self._bot_token

    @bot_token.setter
    def bot_token(self, value):
        with open('bot_keys', 'r') as f:
            value = f.read().strip()
        self._bot_token = value

    async def on_ready(self):
        print(f"Bot is ready")
        await self.change_presence(activity=discord.Game(name='цигу мигу чакарака'))

    async def on_voice_state_update(self, member, before, after):
        if after.channel is None and self._voice_clients.get(member.guild.id):
            if not isinstance(self._voice_clients[member.guild.id], list) and not \
                    self._voice_clients[member.guild.id].is_playing():
                await self.play_next_song(member.guild.id, None)

    async def on_message(self, msg):
        print(f"DEBUG: on_message called with content: {msg.content}")

        if msg.guild:
            try:
                self.guild_id = msg.guild.id
            except AttributeError as at:
                return at

        if msg.content.startswith('$play'):
            if not self._voice_clients.get(self.guild_id):
                try:
                    voice_channel = msg.author.voice.channel
                    voice_client = await voice_channel.connect()

                    self._voice_clients.setdefault(self.guild_id, []).append(voice_client)
                    self.voice_status = 'connected'
                except Exception as err:
                    await msg.channel.send('Влез в music канала.')
                    self.voice_status = 'not connected'
                    print(err)
                    raise NotInVoiceChannel

            try:
                test_for_url = msg.content.split()
                if len(test_for_url) > 1:
                    test_for_url = deque(test_for_url[1:])
                    self.url = ' '.join(test_for_url)
                else:
                    self.url = test_for_url[1]

                if self.url == 'skakauec':
                    self.url = 'https://www.youtube.com/watch?v=pq3C-UE6RE0'
                elif self.url == 'sans':
                    self.url = 'https://www.youtube.com/watch?v=0FCvzsVlXpQ'
                elif self.url == 'ignf':
                    self.url = 'https://www.youtube.com/watch?v=yLnd3AYEd2k'
                elif 'http' not in self.url:
                    self.url = self.find_video_url(self.url)

                self.song_queues.setdefault(self.guild_id, []).append(self.url)
                self.song_queue_name.append(self.get_video_name(self.url))

                video_name = self.get_video_name(self.url)

                if video_name != 'Video title not available' and \
                        video_name != 'Error retrieving video title':
                    await msg.channel.send(f"Добавена песен в плейлиста: {video_name}")
                    self.song_queues[self.guild_id].append(self.url)
                    self.song_queue_name.append(video_name)
                else:
                    await msg.channel.send('Пробуем при намирането на таз песен.')

                if len(self.song_queues[self.guild_id]) == 1 and not self._voice_clients[self.guild_id][
                    -1].is_playing():
                    await self.play_next_song(self.guild_id, msg)
            except yt_dlp.DownloadError:
                await msg.channel.send(f"Нема такова '{str(self.url)}'")
                await self._voice_clients[self.guild_id].disconnect()
                self.voice_status = 'not connected'
            except Exception as err:
                await msg.channel.send("ГРЕДА")
                await self._voice_clients[self.guild_id].disconnect()
                self.voice_status = 'not connected'
                print(err)

    async def play_next_song(self, guild_id, msg):
        print(f"play_next_song called for guild {guild_id}")
        if guild_id in self.song_queues and self.song_queues[guild_id]:
            print(f"HIT 1")
            next_url = self.song_queues[guild_id][0]

            if 'MEGALOVANIA' in MusicBot.get_video_name(next_url):
                print(f"HIT 2")
                self.bot_chat = 'https://tenor.com/view/funny-dance-undertale-sans-gif-26048955'
            elif "I'VE GOT NO FRIENDS" in self.get_video_name(next_url):
                self.bot_chat = 'https://tenor.com/view/actorindie-worlds-smallest-violin-aww-violin-gif-13297153'
            elif 'hipodil' in str(self.get_video_name(next_url)).lower():
                self.bot_chat = 'https://tenor.com/view/cat-music-listening-gif-18335467'
            else:
                self.bot_chat = ''

            if self.bot_chat:
                print(f"HIT 3")
                await msg.channel.send(self.bot_chat)
            else:
                print("HIT 4")
                await msg.channel.send(f"Пущам: {self.get_video_name(next_url)}")

            # Clean up
            print("HIT 5")
            print(f"Voice clients length: {len(self._voice_clients.get(guild_id, []))}")
            self.song_queues[guild_id].pop(0)
            print("HIT 6")
            self.song_queue_name.popleft()

            try:
                next_song = await asyncio.to_thread(self.ytdl.extract_info, next_url, {'download': False})
                next_audio = discord.FFmpegPCMAudio(next_song['url'], **self.ffmpeg_options,
                                                    executable="/usr/bin/ffmpeg")

                print("HIT 7")

                def after_play(e):
                    print(f"after_play called for guild {guild_id}")
                    asyncio.run_coroutine_threadsafe(self.play_next_song(guild_id, msg), self.loop)

                print("HIT 8")
                self._voice_clients[guild_id].on_after(after_play)
                print("HIT 9")
                self._voice_clients[guild_id].play(next_audio)
                print("HIT 10")
                await self.change_presence(activity=discord.Game(name=self.get_video_name(next_url)))
            except Exception as e:
                print(f"Error in play_next_song: {e}")

    """ Helper functions"""

    @staticmethod
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

    def find_video_url(self, search_query):
        ydl_opts = self.yt_dl_opts
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video = ydl.extract_info(f"ytsearch:{search_query}", ie_key='YoutubeSearch')['entries'][0]
            return video['webpage_url']

    async def find_files_to_clean(self):
        """ collects a list of files to be cleaned"""
        self.files_to_clean.clear()
        pattern = os.path.join('.', '*.webm')
        pattern2 = os.path.join('.', '*.opus')
        self.files_to_clean = glob.glob(pattern)
        self.files_to_clean.append(glob.glob(pattern2))

    async def clean_files(self):
        for file in self.files_to_clean:
            os.remove(file)
            print(f"Cleared {file} from local repo")

    def run_bot(self):
        self.run(self.bot_token)


class NotInVoiceChannel(Exception):
    """A custom exception class to raise an error if user is not in a voice channel."""

    def __init__(self, message="User not in voice channel."):
        self.message = message
        super().__init__(self.message)


bot = MusicBot()
bot.run_bot()

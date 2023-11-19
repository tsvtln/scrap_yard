import discord
import pafy
import youtube_dl
from discord.ext import commands
from discord_buttons_plugin import *
import urllib.request
import json
import urllib
from pytube import Playlist
import asyncio

intents = discord.Intents.all()
client = commands.Bot(command_prefix=["?", "/", "komandi"], intents=intents)
TOKEN = 'token here'
buttons = ButtonsClient(client)
song_queue = {}


@client.command()
async def komandi(ctx):
    response = 'Епа де да знам. Пробвай там "p", "r" или за плейлиздже "pl"'
    await ctx.send(response)


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='цигу мигу чакарака'))


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setup()
        self.name_song = ''

    def setup(self):
        for guild in self.bot.guilds:
            song_queue[guild.id] = []

    async def check_queue(self, ctx):
        if len(song_queue[ctx.guild.id]) > 0:
            await self.play_song(ctx, song_queue[ctx.guild.id][0])
            song_queue[ctx.guild.id].pop(0)

    async def search_song(self, amount, song, get_url=False):
        info = await self.bot.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL(
            {"format": "bestaudio", "quiet": True}).extract_info(f"ytsearch{amount}:{song}", download=False,
                                                                 ie_key="YoutubeSearch"))
        if len(info["entries"]) == 0:
            return None

        return [entry["webpage_url"] for entry in info["entries"]] if get_url else info

    async def play_song(self, ctx, song):
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)),
                              after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5
        self.name_song = pafy.new(song).title
        await ctx.send(f":musical_note: `{self.name_song}`")
        await self.play_buttons(ctx)

    @commands.command(aliases=['pl'])
    async def playlist(self, ctx, *, song=None):
        p = Playlist(song)
        for number_songs, song_url in enumerate(p, 1):
            song_queue[ctx.guild.id].append(song_url)
            if number_songs == 20:
                break
        try:
            await ctx.author.voice.channel.connect()
        except ValueError:
            pass
        if song is None:
            return await ctx.send("Тре ми плейлист уе наркоман.\nДай ми примерно `?pl <link на плейлист от тубата>`")

        if ctx.voice_client is None:
            return await ctx.send("Влез в гласов канал да не те вкарам у канафката")

        await self.play_song(ctx, song_queue[ctx.guild.id][0])
        song_queue[ctx.guild.id].pop(0)
        await ctx.send(f"{number_songs} добавени песнички в плейлиЗта!")

    @commands.command(aliases=['p', 's', 'r'])
    async def play(self, ctx, *, song=None):
        try:
            await ctx.author.voice.channel.connect()
        except ValueError:
            pass
        if song is None:
            return await ctx.send("Ама дай име на песен бе тикво.\nПример: `?p Скакауец`")

        if ctx.voice_client is None:
            return await ctx.send("Влез в гласов канал да не те вкарам у канафката")

        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
            result = await self.search_song(1, song, get_url=True)
            if result is None:
                return await ctx.send("Нема такава песен или пък има ама ддз, опраай са.")
            song = result[0]

        if ctx.voice_client.source is not None:
            queue_len = len(song_queue[ctx.guild.id])
            next_song = pafy.new(song).title
            if queue_len < 20:
                song_queue[ctx.guild.id].append(song)
                return await ctx.send(
                    f"Пущам {self.name_song}!\n**{next_song}** добавена в плейлизтята на позиция: {queue_len + 1}.")

            else:
                return await ctx.send(
                    f"Сори мотори, най-много 20 песнички може, чеки **{self.name_song}** да свърши.")

        await self.play_song(ctx, song)


@buttons.click
async def skip_b(ctx):
    await ctx.reply(content="Т'ва беше тая ужасна песен, ся ще пущам друга.",
                    flags=MessageFlags().EPHEMERAL)


@buttons.click
async def list_b(ctx):
    await ctx.reply(content="Плейлистата до момента.", flags=MessageFlags().EPHEMERAL)


@buttons.click
async def resume_b(ctx):
    await ctx.reply(content="Пущам 2ро полувреме.", flags=MessageFlags().EPHEMERAL)


@buttons.click
async def pause_b(ctx):
    await ctx.reply(content="СТОП МАШИНИ.", flags=MessageFlags().EPHEMERAL)


@buttons.click
async def stop_b(ctx):
    await ctx.reply(content="аЙДЕе стига толкоз.", flags=MessageFlags().EPHEMERAL)


@commands.command()
async def play_buttons(ctx):
    await buttons.send(
        content=":tumbler_glass: ОПАЛА!!!",
        channel=ctx.channel.id,
        components=[ActionRow([Button(style=ButtonType().Primary, label="Следваща песен", custom_id="skip_b"),
                               Button(style=ButtonType().Success, label="ПлейлиЗд", custom_id="list_b"),
                               Button(style=ButtonType().Success, label="Палза", custom_id="pause_b"),
                               Button(style=ButtonType().Secondary, label="Пущай пак", custom_id="resume_b"),
                               Button(style=ButtonType().Danger, label="Спри са уе", custom_id="stop_b", )])])


async def setup():
    await client.wait_until_ready()
    await client.add_cog(Player(client))


@client.event
async def on_ready():
    await setup()


@client.event
async def on_message(message):
    ctx = await client.get_context(message)
    if message.content == "Се тая.":
        try:
            del song_queue[ctx.guild.id][:]
        except IndexError:
            print("Нема нищо")
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()
    elif message.content == "Спрех я таа песен. След малко следващата.":
        ctx.voice_client.stop()
    elif message.content == "Пущам пак.":
        if ctx.voice_client is None:
            return await ctx.send("Тре да влеза у некой гласов канал.")
        if not ctx.voice_client.is_paused():
            return await ctx.send("Ша та прибия, пуснал съм вече.")
        ctx.voice_client.resume()
    elif message.content == "Палзичка":
        if ctx.voice_client.is_paused():
            return await ctx.send("Вече съм в палзичка бе братлендзе.")
        ctx.voice_client.pause()
    elif message.content == "Плейлиста е":
        if len(song_queue[ctx.guild.id]) == 0:
            return await ctx.send("ПРАЗЕН")
        embed = discord.Embed(title="ПЛЕЙЛИЗД", description="", colour=discord.Colour.dark_gold())
        for i, url in enumerate(song_queue[ctx.guild.id], 1):
            url_song = url
            params = {"format": "json", "url": url_song}
            url_api = "https://www.youtube.com/oembed"
            query_string = urllib.parse.urlencode(params)
            name = url_api + "?" + query_string
            with urllib.request.urlopen(name) as response:
                response_text = response.read()
                data = json.loads(response_text.decode())
            embed.description += f"{i}. [{data['title']}]({url})\n"
        await ctx.send(embed=embed)

    await client.process_commands(message)


async def main():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: client.add_cog(Player(client)))



def run_bot():
    asyncio.run(main())
    client.run(TOKEN)



if __name__ == "__main__":
    run_bot()

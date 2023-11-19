# Import the required modules
import discord
import os
from discord.ext import commands

# from dotenv import load_dotenv

# Create a Discord client instance and set the command prefix
intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)
token = 'token_here'


# Set the confirmation message when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as Sniffing Bot')


# Set the commands for your bot
@bot.command()
async def greet(ctx):
    response = 'LoFi aka PotKor aka Ceco pi4a'
    await ctx.send(response)


@bot.command()
async def boga_na_dotata(ctx):
    response = 'Ти си бога на Dotata.'
    await ctx.send(response)


@bot.command()
async def list_command(ctx):
    response = 'You can use the following commands: \n !greet \n !list_command \n !functions'
    await ctx.send(response)


@bot.command()
async def functions(ctx):
    response = '*Sniff Sniff*'
    await ctx.send(response)


# Retrieve token from the .env file
# load_dotenv()
bot.run(token)

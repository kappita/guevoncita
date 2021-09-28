import os
import asyncio
import random
from typing import final
import discord
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import Bot
from discord import FFmpegPCMAudio
import pickle
from discord.player import FFmpegOpusAudio
from dotenv import load_dotenv
import youtube_dl
import time
load_dotenv("peo.env")
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()

meses = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
client = discord.Client(intents=intents)
allusers = []
idserver = 881368444791054386
queue = []


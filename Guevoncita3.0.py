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

def check_playlist(queue):
    if len(queue) > 10:
        playlistmessage = 'La playlist es:\n y ' + str(len(queue) - 10) + ' canciones más \n'
        for songplace in range(10):
            playlistmessage += str(10-songplace) + '.- ' + queue[9 - songplace]['title'] + '\n'

    elif len(queue) <= 10 and len(queue) != 0:

        playlistmessage = 'La playlist es: \n'
        for songplace in range(len(queue)):
            playlistmessage += str(len(queue)-songplace) + '.- ' + queue[len(queue) - 1 - songplace]['title'] + '\n'       

    else:
        playlistmessage = 'No hay nada en la cola de reproducción. \nAgrega canciones escribiendo links de YouTube en el chat.'         
    return playlistmessage



def check_queue(voiceclient, playlistchannel):
    global queue
    if queue != []:
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format':"bestaudio"}
        nextsong = queue.pop(0)
        newurl = 'https://www.youtube.com/watch?v=' + nextsong['id']
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            nextsource = ydl.extract_info(newurl, download=False)

        nextaudio = discord.FFmpegOpusAudio.from_probe(nextsource['formats'][0]['url'], **FFMPEG_OPTIONS)
        fut = asyncio.run_coroutine_threadsafe(nextaudio, client.loop)
        try:
            nextaudio = fut.result()
            player = voiceclient.play(nextaudio, after=lambda x=None: check_queue(voiceclient, playlistchannel))
        except:
            pass

        


        embedmessage = 'Ahora estás escuchando: ' + nextsong['title']


        nowplaying = discord.Embed(title=embedmessage)


        nowplaying.set_image(url=nextsource['thumbnails'][-1]['url'])
            

        coro = playlistchannel.edit(content=check_playlist(queue), embed=nowplaying)  
        fut = asyncio.run_coroutine_threadsafe(coro, client.loop)    
        try:
             fut.result()
        except:
            pass
    else:
        embedmessage = 'No estoy tocando nada en este momento. \nColoca alguna canción escribiendo su link de YouTube en el chat'
        nowplaying = discord.Embed(title=embedmessage)
        nowplaying.set_image(url='https://i.ytimg.com/vi/86O_FZ1Ph4I/maxresdefault.jpg')
        coro = playlistchannel.edit(content='', embed=nowplaying)  
        fut = asyncio.run_coroutine_threadsafe(coro, client.loop)    
        try:
             fut.result()
        except:
            pass






## Declares the user object
class disc_user():
    def __init__(self, name, nickname, userid, birthmont, birthday):
        self.name = name
        self.nickname = nickname
        self.id = userid
        self.month = birthmont
        self.day = birthday

#Searches for a save file

try: ##If there's no save file it creates one
    open('allusers.pickle', 'xb')
    load_data = open('allusers.pickle', 'rb')
    print('allusers.pickle no existe. Creando allusers.pickle')
except: ##Uses old data if there's a savefile
    load_data = open('allusers.pickle', 'rb')
    print('allusers.pickle existe. load_data = allusers.pickle')


## Sets bot's configuration 
@client.event
async def on_ready():
    global allusers
    testguild = client.get_guild(idserver)
    game = discord.Game('Javier Salazar chúpamela')
    await client.change_presence(activity=game)


    print('Güevoncita se conectó')
    ##Searches for old data
    try: ##Uses the data found in the save file
        previouslist = pickle.load(load_data)
        allusers = previouslist
        print('allusers.pickle tenía información anterior. Utilizando la información anterior')
        ##checks for discrepancies between the userlist and the users in the guild
        for member in testguild.members:
            existent = False
            for x in range(len(allusers)):
                if allusers[x].id == member.id:
                    existent = True
            if existent == False:
                allusers.append(disc_user(member.name, member.nick, member.id, '', ''))
            

    except: ## Creates new data if there's no information in the save file
        print('allusers.pickle no tenía información anterior. Creando datos')

        for member in testguild.members:
            if member.bot == False:
                allusers.append(disc_user(member.name, member.nick, member.id, '', ''))

    music_channel = client.get_channel(id=890351893224755220)

    old_messages = await music_channel.history(limit=200).flatten()

    for oldmessage in old_messages:
        if oldmessage.id == 890656762594725908 or oldmessage.id == 890656775915835392:
            pass
        else:
            await oldmessage.delete()


#Creates a user when someone joins
@client.event
async def on_member_join(member):
    allusers.append(disc_user(member.name, member.nick, member.id, '', ''))

##Removes user from the database when the user leaves the guild
@client.event
async def on_member_remove(member):
    for user in range(len(allusers)):
        if allusers[user].id == member.id:
            allusers.pop(user)



@client.event
async def on_message(message):
    global allusers
    global queue
    print('Mensaje recibido')

    ## Ignores the message if the author is the bot
    if message.author == client.user:
        return

    if message.channel.id == 890351893224755220: 
        consolemessage = await message.channel.fetch_message(id=890656775915835392)
        await message.delete()
        try:
            vc = client.voice_clients[0]

        except:
            try:
                vc = await message.author.voice.channel.connect()

            except:
                errormessage = await message.channel.send('Debes estar conectado a un canal')
                await errormessage.delete(delay=3)
                return

        if message.content == 'pause' or message.content == 'pausa':
            vc.stop()

        elif message.content == 'resume':
            vc.resume()

        elif message.content == 'skip':
            vc.stop()

        elif message.content == 'clear':
            queue = []
            await consolemessage.edit(content='No hay nada en la cola de reproducción. \nAgrega canciones escribiendo links de YouTube en el chat.')

        else:
            url = message.content
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            YDL_OPTIONS = {'format':"bestaudio", 'extract_flat': True, 'writethumbnail' : True, 'playlistend':15, 'default_search':'auto', 'skip_download':True}

            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)


            if '_type' in info:
                for song in info['entries']:
                    
                    queue.append({'id': song['id'], 'title':song['title']})
            else:
                queue.append({'id': info['id'], 'title':info['title']})

            
            if vc.is_playing() == False:
                YDL_OPTIONS = {'format':"bestaudio"}
                firstsong = queue.pop(0)
                newurl = 'https://www.youtube.com/watch?v=' + firstsong['id']
                with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                    firstsource = ydl.extract_info(newurl, download=False)

                source = await discord.FFmpegOpusAudio.from_probe(firstsource['formats'][0]['url'], **FFMPEG_OPTIONS)
                vc.play(source, after=lambda x=None: check_queue(vc, consolemessage))       

                embedmessage = 'Ahora estás escuchando: ' + firstsong['title']


                nowplaying = discord.Embed(title=embedmessage)


                nowplaying.set_image(url=firstsource['thumbnails'][-1]['url'])
                        

                await consolemessage.edit(content=check_playlist(queue), embed=nowplaying)  


            elif vc.is_playing() == True:       


                await consolemessage.edit(content=check_playlist(queue))  





    else:
        ##Strips the content of the message to be processed
        stripped = message.content.split(' ')
        ##Checks the content of the message 
        if stripped[0] == "&cum": ##ignores the message if it doesn't have the command prefix

            date = stripped[1].split('/') ##Creates a date based on the content of the message
            date = [int(date[0]), int(date[1])]
            for x in range(len(allusers)): ##Adds the date to the user data
                if allusers[x].id == message.author.id:
                    allusers[x].day = date[0]
                    allusers[x].month = date[1]
            newsave = open('allusers.pickle', 'wb') ##Saves the data into the save file
            pickle.dump(allusers, newsave) 
            newsave.close()
            ##Sorts the users based on their birthday
            sortedbirth = []
            for month in range(1, 13):
                for day in range(1, 32):
                    for x in range(len(allusers)):
                        if allusers[x].month == '' :
                            pass
                        elif allusers[x].month == month and allusers[x].day == day:
                            sortedbirth.append(allusers[x])

            ## Initial string for the final message
            felizcum = str('')
            ## Creates the message with all the birthdays
            for x in range(len(sortedbirth)):
                print(sortedbirth[x].name)
                felizcum = felizcum + sortedbirth[x].name + ': ' + str(sortedbirth[x].day) + ' de ' + meses[sortedbirth[x].month] + '\n' 

            cumchannel = discord.utils.get(client.get_all_channels(), guild__name='Güevoncitos', name='guevoncita-beta')
            cumessage = await cumchannel.fetch_message(id=888999046344241183)
            embed = discord.Embed(title='Cums', description=felizcum, colour=0xaa1a1a)
            embed.set_thumbnail(url='https://3.bp.blogspot.com/_cd6_MFUGTUE/TI-qhkYbt0I/AAAAAAAAAV8/wJHhnJVi8Lo/s400/the_cake_is_a_lie_portal.jpg')
            await cumessage.edit(embed=embed)

        
        
        
        if message.channel.id == 888997979992784907:
            print(message.content)
            await message.delete()


client.run(TOKEN)


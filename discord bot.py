import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import asyncio
import youtube_dl
from youtubesearchpython import SearchVideos
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
from itertools import cycle

bot = commands.Bot(command_prefix = '%')

status=cycle(["Velai Illa Pattathari","3","Kodi","Pattas","Yaaradi Nee Mohini","Asuran"])

@bot.event
async def on_ready():
    changemovies.start()
    print("good to go")

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to discord...\n")


@bot.event
async def on_command_error(ctx , error):
    await ctx.send(f'abbey panni {ctx.message.author.mention}')
    await ctx.send(error)

load_dotenv()
servers = ('754716663529734254','674567305291890698')
song_list = dict.fromkeys(servers,[])
Pause_list = dict.fromkeys(servers, False)

@bot.command(aliases=['seru'])
async def join(ctx):
    global song_list
    global Pause_list
    song_list[ctx.guild.id] = []
    Pause_list[ctx.guild.id] = False
    if ctx.guild.voice_client in bot.voice_clients:
        await ctx.send('i am already in vc u blind donkey')
        return
    try:
        await ctx.message.author.voice.channel.connect()
        await ctx.send('AHHHH,ENJOY')
    except:
        await ctx.send('Rascal, VC u need to join faggot')

@bot.command(aliases=['kalikukka','p'])
async def play(ctx,*args):
    
    if  ctx.message.author.voice!=None and (ctx.guild.voice_client in bot.voice_clients):
        
        global song_list
        global Pause_list
        songa = ' '.join(args)
        
        if 'https://open.spotify.com/' in songa:
            songa = spotify_queue(ctx,songa)
        else:
            song_list[ctx.guild.id].append(songa)

        if len(song_list[ctx.guild.id])!=1 or ctx.message.guild.voice_client.is_playing()==True or Pause_list[ctx.guild.id]==True:
            await ctx.send(f'**`{songa}` added in queue u impatient monkey**')

        if ctx.message.guild.voice_client.is_playing()==False and Pause_list[ctx.guild.id]==False:
           download(ctx,ctx.message.guild.voice_client,ctx.guild.id)

    else:
        await ctx.send('Rascal, VC u need to join faggot,')       

def download(ctx,voice_client,server_id):
    asyncio.run_coroutine_threadsafe(playing_song(ctx,voice_client,server_id),bot.loop)
    pass

async def playing_song(ctx,voice_client,server_id):

    global song_list
    radio = {'HiFM':os.getenv('HiFM'),
            'Merge':os.getenv('Merge'),
            'Virgin':os.getenv('Virgin') }
    
    try:
        song = song_list[server_id][0]
    except:
        return
    song_list[server_id].pop(0)

    if song in radio.keys():
        voice_client.play(discord.FFmpegPCMAudio(radio[song]),after =lambda e: download(ctx,voice_client,server_id))
        await ctx.send(f'Now Playing : {song} Radio') 
        return
    
    results = SearchVideos(song,offset=1,mode='dict',max_results=1)
    x = results.result()
    for I in x['search_result']:

        ytdl_format_options = {
                'format' : 'bestaudio/best' ,
                'postprocessors' : [{
                       'key' : 'FFmpegExtractAudio' ,
                       'preferredcodec' : 'mp3' ,
                       'preferredquality' : '192' ,
                       }]
                }

        ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
        #ytdl.download([I['link']])
    
    embed = discord.Embed(title=f"*ab suno\n`{I['title']}`\naur apna manorajan karo*", colour=discord.Colour.red())
    embed.set_thumbnail(url = I['thumbnails'][0])
    embed.add_field( name='Duration' , value = I['duration'])
    await ctx.send(embed=embed)

    if voice_client.is_playing()==False:

        audio = ytdl.extract_info(I['link'],download = False)
        streamable_url = audio['formats'][0]['url']
        before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        voice_client.play(discord.FFmpegPCMAudio(streamable_url,before_options = before_options),after =lambda e: download(ctx,voice_client,server_id))

    else:
        return

def spotify_queue(ctx,link):
    global song_list
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.getenv('Spotify_id'),client_secret=os.getenv('Spotify_secret')))
    L = link.split('/')
    if 'https://open.spotify.com/playlist/' in link:
        tracks = sp.playlist_tracks(L.pop())
        for I in tracks['tracks']['items']:
            song_list[ctx.guild.id].append(I["track"]["name"])
        return f"{tracks['total']} gaane from spotify playlist"
    elif 'https://open.spotify.com/track/' in link:
        track = sp.track(L.pop())
        song_list[ctx.guild.id].append(track['name'])
        return track['name']
                          
@bot.command(aliases=['line','q'])
async def queue(ctx):
    global song_list
    if  ctx.message.author.voice!=None:
        if song_list[ctx.guild.id] == []:
            await ctx.send('jab koi line he hi nahi to kya dekho ge be')
            return
        for i,s in enumerate(song_list[ctx.guild.id]):
            await ctx.send(f'*{i+1})*: **`{s}`**')
    else:
        await ctx.send('abbe mandbuddhi, VC to join karo')
        
@bot.command(aliases = ['hatt','r'])
async def remove(ctx,position : int):
    global song_list
    if  ctx.message.author.voice!=None:
        if song_list[ctx.guild.id] == []:
            await ctx.send('jab koi line he hi nahi to kya hatao ge be')
            return
        try :
            await ctx.send(f'kya yaar, `{song_list[ctx.guild.id][position-1]}` humse hi hatwana tha')
            song_list[ctx.guild.id].pop(position-1)
        except:
            await ctx.send('ek minute... ye kya, tumhara to number hi line ke bahar he')
    else:
        await ctx.send('abbe mandbuddhi, VC to join karo')
    
@bot.command(aliases = ['niruthu'])
async def pause(ctx):
    global Pause_list
    if ctx.message.author.voice == None:
        await ctx.send('abbe mandbuddhi, VC to join karo')
        return
    ctx.message.guild.voice_client.pause()
    Pause_list[ctx.guild.id] = True
    await ctx.send('kya yaar beech me rok kar poora maza kharab kar diye')
    
@bot.command(aliases = ['thodurum'])
async def resume(ctx):
    global Pause_list
    if ctx.message.author.voice == None:
        await ctx.send('abbe mandbuddhi, VC to join karo')
        return
    ctx.message.guild.voice_client.resume()
    Pause_list[ctx.guild.id] = False
    await ctx.send('je hui na baat ab maze karo')

@bot.command(aliases = ['poda_patti','s'])
async def skip(ctx):
    global Pause_list
    if ctx.message.author.voice == None:
        await ctx.send('abbe mandbuddhi, VC to join karo')
        return
    Pause_list[ctx.guild.id] = False
    ctx.message.guild.voice_client.stop()
    await ctx.send('kya yaar, itne badhiya gane ko hata diya')
   
@bot.command(aliases = ['poda','d'])
async def disconnect(ctx):
    global Pause_list
    global song_list
    for x in bot.voice_clients:
        if(x.guild == ctx.message.guild):
            song_list[ctx.guild.id]=[]
            Pause_list[ctx.guild.id] = False
            await ctx.send('phir milte he')
            return await x.disconnect()
    if bot.voice_clients==[]:
        await ctx.send('abbe hum gaye hi kab jo tum humko nikaloge')

@bot.command()
async def kick(ctx, member : discord.Member):
    await member.kick(reason = None)
    await ctx.send(f'{member.mention} ko dhakke maar ke nikal diye he be')

@bot.command()
async def b(ctx , no : int):
    await ctx.message.channel.purge(limit=no)


                                 
@bot.command()
async def ping(ctx):
    await ctx.send(f'rukawat ki khed he\nping : {round(bot.latency,2)}')

@bot.command()
async def nandri(ctx):
    if ctx.message.author.id == 689110105878560795 :
        await ctx.send('Puriyuthu')
        await ctx.bot.logout()
    else :
        await ctx.send('panni,do u have common sense')

@tasks.loop(seconds=3)
async def changemovies():
    await client.change_presence(activity=discord.Game(next(status)))

token=os.getenv('token')
bot.run(token)

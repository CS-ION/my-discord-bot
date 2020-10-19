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
import sports
from pycricbuzz import Cricbuzz
import tracemalloc

tracemalloc.start()

bot = commands.Bot(command_prefix = '%')


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
        await ctx.send('VC join pannu pannadai')

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
    
    embed = discord.Embed(title=f"*Ippodu Kelungal:)\n`{I['title']}`\naur apna manorajan karo*", colour=discord.Colour.red())
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
            await ctx.send('Line ella parrgu enna parkirgal pannadai')
            return
        for i,s in enumerate(song_list[ctx.guild.id]):
            await ctx.send(f'*{i+1})*: **`{s}`**')
    else:
        await ctx.send('Rascal, VC u need to join faggot')
        
@bot.command(aliases = ['hatt','r'])
async def remove(ctx,position : int):
    global song_list
    if  ctx.message.author.voice!=None:
        if song_list[ctx.guild.id] == []:
            await ctx.send('Line ella parrgu enna parkirgal pannadai')
            return
        try :
            await ctx.send(f'kya yaar, `{song_list[ctx.guild.id][position-1]}` humse hi hatwana tha')
            song_list[ctx.guild.id].pop(position-1)
        except:
            await ctx.send('Oru minute, enna idhu , unga number line ka vellila irkudhu')
    else:
        await ctx.send('Rascal, VC u need to join faggot')
    
@bot.command(aliases = ['niruthu'])
async def pause(ctx):
    global Pause_list
    if ctx.message.author.voice == None:
        await ctx.send('Rascal, VC u need to join faggot')
        return
    ctx.message.guild.voice_client.pause()
    Pause_list[ctx.guild.id] = True
    await ctx.send('Idiot, nirithu indha nonsense')
    
@bot.command(aliases = ['thodurum'])
async def resume(ctx):
    global Pause_list
    if ctx.message.author.voice == None:
        await ctx.send('Rascal, VC u need to join faggot')
        return
    ctx.message.guild.voice_client.resume()
    Pause_list[ctx.guild.id] = False
    await ctx.send('Mudhinjudu enjoy pannuga')

@bot.command(aliases = ['poda_patti','s'])
async def skip(ctx):
    global Pause_list
    if ctx.message.author.voice == None:
        await ctx.send('Rascal, VC u need to join faggot')
        return
    Pause_list[ctx.guild.id] = False
    ctx.message.guild.voice_client.stop()
    await ctx.send('ENNNA DA NEE NALLA SONG ELLA DELETE PANNARA')
   
@bot.command(aliases = ['poda','d'])
async def disconnect(ctx):
    global Pause_list
    global song_list
    for x in bot.voice_clients:
        if(x.guild == ctx.message.guild):
            song_list[ctx.guild.id]=[]
            Pause_list[ctx.guild.id] = False
            await ctx.send('Paakalam panni')
            return await x.disconnect()
    if bot.voice_clients==[]:
        await ctx.send('Neega ponaadhanai naanu poooga mudhiyum')

@bot.command()
async def kick(ctx, member : discord.Member):
    await member.kick(reason = None)
    await ctx.send(f'{member.mention} gucci , sorry')

@bot.command()
async def b(ctx , no : int):
    await ctx.message.channel.purge(limit=no)

@bot.command()
async def member_count(ctx):
        await ctx.send(ctx.message.guild.member_count)
        
@bot.command()
async def all_members(ctx):
    duplicate = []
    for I in bot.get_all_members():
        if ctx.guild == I.guild:
            if I.name in duplicate:
                continue
            await ctx.send(I.name)
            duplicate.append(I.name)

@bot.command()
async def change(ctx, member : discord.Member, *args):
    new = ' '.join(args)
    await member.edit(nick = new)


@bot.command()
async def dp(ctx, user: discord.User = None):
    if user==None:
        user = ctx.message.author
    await ctx.send(user.avatar_url_as())
    
@bot.command()
async def Q(ctx,*args):
    question= ' '.join(args)
    for j in search(question, tld="co.in", num=1, stop=1, pause=2):
         await ctx.send(j)


@bot.command()
async def hit(ctx,arg):
    hit = {
    'krishna': 'Yarukku pudikadhu? Naai punnaiku kudhadha amma na pudikkum',
    'vivek' : 'Vazhkaila namma enjoy pannura velaya seiyyanum. Ilana sethranum” ',
    'ramanan' : 'Senjuruven',
    'ramil' : 'Ennae maari pasangala paartha pudikkaathu, paakka paakka thaan pudikkum',
    'harshal' : 'Actualla naan konjam bad boy sir',
    'rounak' : 'Amul Baby, Raghuvaranae ithuvaraikkum nee villain ah thaane paarthirukkae, hero va paarthathillaye, inimae paarppae',
    'ayaan' : 'Naanga ellam tsunami laye swimming eh podravanga',
    'abishai':'If you are bad, I am your dad',
    'jerin' : 'Madam, singathukku vaala irukkarathae vida naan punaikku thalayave irundhidaren!',
    'shane' : 'Vanthathu vaazhnthathu senjathu serthathungarathae vida nammalukkappram enna ninnathungarathu thaanda matteru!',
    'vineet' : 'ahh iam eating chicken fry unnaku venuma',
    }
    await ctx.send(hit.get(arg.lower(),"Pannadai endha karmu pottai <:abeysaale:731486907208433724>"),tts = True)    
@bot.command()
async def pingu(ctx, member:discord.Member):
    if member.discriminator == '0994':
        await ctx.send('poda patti')
        return
    n=0
    while n<10:
        await ctx.send(member.mention)
        n=n+1           
@bot.command()
async def everyone(ctx):

    L = [os.getenv('Vivek'),
    os.getenv('Dannyboi'),
    os.getenv('ValdyFox'),
    os.getenv('FractalsAreBae'),
    os.getenv('Silent_Killer'),
    os.getenv('SKULL_TROOPER'),
    os.getenv('jetso'),
    os.getenv('yallaboi'),]
    for I in L:
        if I == ctx.message.author.id :
            continue
        await ctx.send(f'<@!{I}>')
@bot.command()
async def poll(ctx,*args,):
    embed = discord.Embed(title = f"POLLING\n{' '.join(args)}" , colour = discord.Colour.red())
    embed.description = f"YES:regional_indicator_y:  \n\nNO :regional_indicator_n:  "
    #embed.set_image(url = 'https://th.thgim.com/migration_catalog/article11163206.ece/alternates/FREE_435/modi%20symbol%27)
    message = await ctx.send(embed = embed)
    await message.add_reaction(emoji='U+1F44D')
    await message.add_reaction(emoji='U+1F44E')
    
@bot.command()
async def ipl(ctx):
    matches = sports.get_sport(sports.CRICKET)
    for match in matches:
        if match.league == 'IND-IPL':
            if match.match_time == 'Match Finished':
                await ctx.send('abe saale abhi to koi game nahi chal raha hai')
                return
            embed = discord.Embed(title='IPL 2020', colour=discord.Colour.gold())
            embed.add_field(name=match.away_team , value=match.away_score , inline = False)
            embed.add_field(name=match.home_team , value=match.home_score , inline = False)
            await ctx.send(embed = embed)
            return
@bot.command()
async def current_score(ctx):   
    match = Cricbuzz()
    try:
        details = match.livescore(match_id())
        embed1 = discord.Embed(title=f"Current Batting Team : {details['batting']['team']}", colour=discord.Colour.red())
    except:
        await ctx.send('abe saale abhi to koi game nahi chal raha hai')
        return

    embed1.add_field(
            name = f"Batsman Name : {details['batting']['batsman'][0]['name']}",
            value = f"Runs Scored : {details['batting']['batsman'][0]['runs']}\n"
            f"Balls Faced : {details['batting']['batsman'][0]['balls']}\n"
            f"Fours Hit : {details['batting']['batsman'][0]['fours']}\n"
            f"Sixes Hit : {details['batting']['batsman'][0]['six']}\n",
            inline = False)
    
    embed1.add_field(
            name = f"Batsman Name : {details['batting']['batsman'][1]['name']}",
            value = f"Runs Scored : {details['batting']['batsman'][1]['runs']}\n"
            f"Balls Faced : {details['batting']['batsman'][1]['balls']}\n"
            f"Fours Hit : {details['batting']['batsman'][1]['fours']}\n"
            f"Sixes Hit : {details['batting']['batsman'][1]['six']}\n",
            inline = False)
    
    await ctx.send(embed = embed1)

    embed2 = discord.Embed(title=f"Current Bowling Team : {details['bowling']['team']}", colour=discord.Colour.green())
    
    embed2.add_field(
        name = f"Bowler Name : {details['bowling']['bowler'][0]['name']}",
        value = f"Overs Done : {details['bowling']['bowler'][0]['overs']}\n"
        f"Runs Given : {details['bowling']['bowler'][0]['runs']}\n"
        f"Wickets Taken : {details['bowling']['bowler'][0]['wickets']}",
        inline = False)
    
    await ctx.send(embed = embed2)    

def match_id():
    c = Cricbuzz()
    matches = c.matches()
    for I in matches:
        if I['srs']=='Indian Premier League 2020' and (I['mchstate']=='toss' or I['mchstate']=='inprogress' or I['mchstate']=='innings break'):
            return I['id']
@bot.command()
async def teams(ctx):
    c = Cricbuzz()
    try:
        I = c.matchinfo(match_id())
    except:
        await ctx.send('abe saale abhi to koi game nahi chal raha hai')
        return
    embed1 = discord.Embed(title= I['team1']['name'], colour=discord.Colour.blue())
    for X,J in enumerate(I['team1']['squad']):
        embed1.add_field(name = J,value = f'{X+1}',inline = False)
    embed2 = discord.Embed(title= I['team2']['name'], colour=discord.Colour.gold())
    for X,J in enumerate(I['team2']['squad']):
        embed2.add_field(name = J,value = f'{X+1}',inline = False)
    await ctx.send(embed = embed1)
    await ctx.send(embed = embed2) 

@bot.command()
async def status(ctx):
    c = Cricbuzz()
    try:
        I = c.matchinfo(match_id())
    except:
        await ctx.send('abe saale abhi to koi game nahi chal raha hai')
        return
    await ctx.send(I['status'])

@bot.command()
async def toss(ctx):
    c = Cricbuzz()
    try:
        I = c.matchinfo(match_id())
    except:
        await ctx.send('abe saale abhi to koi game nahi chal raha hai')
        return
    await ctx.send(I['toss'])

@bot.command()
async def venue(ctx):
    c = Cricbuzz()
    try:
        match = c.matchinfo(match_id())
    except:
        await ctx.send('abe saale abhi to koi game nahi chal raha hai')
        return
    match = c.matchinfo(match_id())
    await ctx.send(match["venue_name"])
    await ctx.send(match['venue_location'])
    
@bot.command()
async def score_card(ctx):
    c = Cricbuzz()
    try:
        scorecard = c.scorecard(match_id())['scorecard'][0]
    except:
        await ctx.send('abe saale abhi to koi game nahi chal raha hai')
        return

    embed1 = discord.Embed(title = f"Batting Team : {scorecard['batteam']}" , colour=discord.Colour.blue())
    embed1.description = f"Score {scorecard['runs']}/{scorecard['wickets']}, Overs {scorecard['overs']}"
    for I in scorecard['batcard']:
        embed1.add_field(
                        name=I['name'],
                        value=f"Runs{I['runs']}\n"
                        f"Balls Faced {I['balls']}\n"
                        f"Fours {I['fours']}\n"
                        f"Sixes {I['six']}\n"
                        f"{I['dismissal']}",
                        inline = False)

    embed2 = discord.Embed(title = f"Bowling Team : {scorecard['bowlteam']}" , colour=discord.Colour.gold())
    for I in scorecard['bowlcard']:
        embed2.add_field(
                        name=I['name'],
                        value=f"Overs : {I['overs']}\n"
                        f"Maidens : {I['maidens']}\n"
                        f"Runs Given : {I['runs']}\n"
                        f"Wickets Taken : {I['wickets']}\n"
                        f"wides : {I['wides']}\n"
                        f"no balls : {I['nballs']}",
                        inline = False)
    
    await ctx.send(embed = embed1)
    await ctx.send(embed = embed2)

@bot.command()
async def prev_match(ctx):
    c = Cricbuzz()
    matches = c.matches()
    for I in matches:
        if I['srs']=='Indian Premier League 2020' and I['mchstate']=='mom':
            embed = discord.Embed(title = f"{I['team1']['name']} vs {I['team2']['name']}" , colour = discord.Colour.blue())
            embed.description = f"{I['status']}"
            await ctx.send(embed = embed)

@bot.command()
async def next_match(ctx):
    c = Cricbuzz()
    matches = c.matches()
    for I in matches:
        if I['srs']=='Indian Premier League 2020' and I['mchstate']=='preview':
            embed = discord.Embed(title = f"{I['team1']['name']} vs {I['team2']['name']}" , colour = discord.Colour.blue())
            embed.description = f"{I['status']}"
            await ctx.send(embed = embed)

@bot.command()
async def ipl_poll(ctx):
    c = Cricbuzz()
    matches = c.matches()
    for I in matches:
        if I['srs']=='Indian Premier League 2020' and (I['mchstate']=='inprogress' or I['mchstate']=='preview'):
            embed = discord.Embed(title = f"IPL POLLING\n{I['team1']['name']} vs {I['team2']['name']}" , colour = discord.Colour.blue())
            embed.description = f"{I['team1']['name']} : 1️⃣\n\n{I['team2']['name']} : 2️⃣ "
            await ctx.send(embed = embed)
  
@bot.command()
async def football(ctx,*args):
    if args == ():
        matches = sports.get_sport(sports.SOCCER)
        embed = discord.Embed(title = 'LIVE MATCHES', colour=discord.Colour.blurple()) 
        for I in matches:
            embed.add_field( name = f'{I}', value =  f'{I.league}')
        await ctx.send(embed = embed)
        return
    try:
        match = sports.get_match(sports.SOCCER, args[0], args[2])
    except:
        await ctx.send('abe shuru to hone do')
        return
    embed = discord.Embed(title = ' '.join(args).upper(), colour=discord.Colour.blurple()) 
    embed.description = f'{match.league}'
    embed.add_field( name = f'{match.away_team}', value =  f'{match.away_score}')
    embed.add_field( name = f'{match.home_team}' , value = f'{match.home_score}')
    await ctx.send(embed = embed)        
                                 
@bot.command()
async def ping(ctx):
    await ctx.send(f'Gucci\nping : {round(bot.latency,2)}'
                   "<a:cat_vibing:753973817608634468>")

@bot.command()
async def nandri(ctx):
    if ctx.message.author.id == 689110105878560795 :
        await ctx.send('Puriyuthu BOSS'
                       "<a:crab_rave:753654717506256937>")
        await ctx.bot.logout()
    else :
        await ctx.send('panni,do u have common sense')

status=cycle(["Velai Illa Pattathari","3","Kodi","Pattas","Yaaradi Nee Mohini","Asuran","Maari"])

@bot.event
async def on_ready():
    changemovies.start()
    print(f"{bot.user} has connected to discord...\n")

        

@tasks.loop(seconds=3)
async def changemovies():
    await bot.change_presence(activity=discord.Game(next(status)))

token=os.getenv('token')
bot.run(token)

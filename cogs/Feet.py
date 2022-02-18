import asyncio
import discord, random, time
import os
import asyncio
from ffmpeg.ffmpeg import FFmpeg
from discord.ext import commands

# images = os.path.join(os.path.dirname(__file__), "feet/")
# images_list = [images + c for c in os.listdir(images)]

class Feet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded - rawr')

    # @commands.command(name='Feet')
    # async def feet(self, ctx):
    #     await ctx.send(file=discord.File(random.choice(Feetpix)))




    # @commands.command(name = "feet", aliases=["aliase"])
    # async def feet(self, ctx:commands.Context):
    #     await discord.Client.send(file=discord.File(random.choice(images)))

    # @commands.command(
    #     name='fard',
    #     description='fard')
    # async def fart(self, ctx, *, voice_channel: discord.VoiceChannel=None):
    #     # grab the user who sent the command
    #     await ctx.send('farding in progress...')
    #     user = ctx.message.author
    #     voice_channel = ctx.author.voice.channel
    #     channel=None
    #     # only play music if user is in a voice channel
    #     if voice_channel!= None:
    #         # grab user's voice channel
    #         channel=voice_channel.name
    #         await discord.Client.say('User is in channel: '+ channel)
    #         # create StreamPlayer
    #         vc= await discord.Client.join_voice_channel(voice_channel)
    #         player = vc.create_ffmpeg_player('vuvuzela.mp3', after=lambda: print('done'))
    #         player.start()
    #         while not player.is_done():
    #             await asyncio.sleep(1)
    #         # disconnect after the player has finished
    #         player.stop()
    #         await vc.disconnect()
    #     else:
    #         await ctx.send('User is not in a channel.')


    # @commands.command()
    # async def fardtest(ctx,song : str):
    #     channel = ctx.author.voice.channel
    #     voice = discord.utils.get(commands.Bot.voice_clients, guild=ctx.guild)
    
    #     if voice is None or not voice.is_connected():
    #         await channel.connect()
    #         voice = discord.utils.get(commands.Bot.voice_clients, guild=ctx.guild)
        
        
    #     song_there = os.path.isfile("Fard\\{}.mp3".format(song))
    #     if song_there == True:
    #         voice.play(discord.FFmpegPCMAudio(('Fard\\{}.mp3'.format(song))))
    #         await ctx.send('{} playing! <:white_check_mark:853651360666877972>'.format(song))
    #     else:
    #         await ctx.send("This file does not exists")




    #     if not channel:
    #                 try:
    #                     channel = ctx.author.voice.channel
    #                 except AttributeError:
    #                     embed = discord.Embed(title="", description="no fard channel to join :(", color=discord.Color.green())
    #                     await ctx.send(embed=embed)

    #             vc = ctx.voice_client

    #             if vc:
    #                 if vc.channel.id == channel.id:
    #                     return
    #                 try:
    #                     await vc.move_to(channel)
    #                 except asyncio.TimeoutError:
    #                     print(f'Moving to channel: <{channel}> timed out.')
    #                     await ctx.send(f'fardin to <{channel}> timed out.')
    #             else:
    #                 try:
    #                     await channel.connect()
    #                 except asyncio.TimeoutError:
    #                     print(f'Connecting to channel: <{channel}> timed out.')
    #                     await ctx.send(f'fardin to <{channel}> timed out.')
    #             await ctx.send(f'**farding in `{channel}`...**')



    @commands.command(name="fartpls")
    async def fartpls(self, ctx, *, channel: discord.VoiceChannel=None):
        # Gets voice channel of message author
        voice_channel = ctx.author.channel
        channel = None
        if voice_channel != None:
            channel = voice_channel.name
            vc = await voice_channel.connect()
            vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="C:<path_to_file>"))
            # Sleep while audio is playing.
            while vc.is_playing():
                time.sleep(.1)
            await vc.disconnect()
        else:
            await ctx.send(str(ctx.author.name) + "is not in a channel.")
        # Delete command after the audio is done playing.
        await ctx.message.delete()


    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send(f"pls work {round(self.bot.latency * 1000) }ms")

def setup(bot):
    bot.add_cog(Feet(bot))
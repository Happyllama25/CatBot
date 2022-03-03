import asyncio
import disnake, random, time
import os
import asyncio
from ffmpeg.ffmpeg import FFmpeg
from disnake.ext import commands

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
    #     await ctx.send(file=disnake.File(random.choice(Feetpix)))

    @commands.command()
    async def join(self, ctx, *, channel: disnake.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""
        await self.ensure_voice(ctx)
        source = disnake.PCMVolumeTransformer(disnake.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print(f"Player error: {e}") if e else None)

        await ctx.send(f"Now playing: {query}")


    @commands.command(name="fartpls")
    async def fartpls(self, ctx, *, channel: disnake.VoiceChannel=None):
        # Gets voice channel of message author
        if not channel:
                    try:
                        channel = ctx.author.voice.channel
                    except AttributeError:
                        embed = disnake.Embed(title="", description="no fard channel to join :(", color=disnake.Color.green())
                        await ctx.send(embed=embed)

                    vc = ctx.voice_client

                    if vc:
                        if vc.channel.id == channel.id:
                            return
                        try:
                            await vc.move_to(channel)
                        except asyncio.TimeoutError:
                            print(f'Moving to channel: <{channel}> timed out.')
                            await ctx.send(f'fardin to <{channel}> timed out.')
                    else:
                        try:
                            await channel.connect()
                        except asyncio.TimeoutError:
                            print(f'Connecting to channel: <{channel}> timed out.')
                            await ctx.send(f'fardin to <{channel}> timed out.')
                    await ctx.send(f'**farding in `{channel}`...**')



                    voice_channel = channel
                    channel = None
                    if voice_channel != None:
                        channel = voice_channel.name
                        vc = await voice_channel.connect()
                        vc.play(disnake.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="C:<path_to_file>"))
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
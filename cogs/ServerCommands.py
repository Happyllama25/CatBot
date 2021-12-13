from discord.ext import commands
import subprocess, discord, asyncio
from time import sleep

class ServerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')

    @commands.command(name='ping')
    async def ping(self, ctx: commands.Context):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000) }ms")

    @commands.command(aliases=['old'])
    async def startold(self, ctx): 
        subprocess.Popen(r'D:\server-dont-delete-ffs\building_server\start.bat', cwd=r'D:\server-dont-delete-ffs\building_server', shell=True)
        embed=discord.Embed(color=0x5f0aee,
        description='Server Starting...')
        embed.set_footer(text='Join on port 25566')
        await ctx.send(embed=embed)

    @commands.command(aliases=['hardcore', 'hard'])
    async def starthard(self, ctx): 
        subprocess.Popen(r'C:\Users\fabse\Desktop\Creations\Python\Servers\hardcore\start.bat', cwd=r'C:\Users\fabse\Desktop\Creations\Python\Servers\hardcore', shell=True)
        embed=discord.Embed(color=0x5f0aee,
        description='Server Starting...')
        embed.set_footer(text='Join with default ip (no port)')
        await ctx.send(embed=embed)

    @commands.command(name='start', aliases=['starty', 'bored', 'mc', 'join', 'ip'])
    async def start(self, ctx): 
        embed=discord.Embed(title='View the Map in Browser',
        url='http://73.49.109.86:8100/',
        color=0x5f0aee,
        description='Server is **always turned on**!')
        embed.set_footer(text='Join at: **73.49.109.86**')
        await ctx.send(embed=embed)

    # @commands.command()
    # async def startsibbi(self, ctx): 
    #     subprocess.Popen(r'C:\Users\fabse\Desktop\Creations\Servers\sibbi-survival\start.bat', cwd=r'C:\Users\fabse\Desktop\Creations\Servers\sibbi-survival', shell=True)
    #     embed=discord.Embed(color=0x5f0aee,
    #     description='Server Starting...')
    #     await ctx.send(embed=embed)

    @commands.command(aliases=['modded', 'mods'])
    async def startmodded(self, ctx): 
        subprocess.Popen(r'C:\Users\fabse\Desktop\Creations\Python\Servers\ldoh_0.3.1_serverpack\start.bat', cwd=r'C:\Users\fabse\Desktop\Creations\Python\Servers\ldoh_0.3.1_serverpack', shell=True)
        embed=discord.Embed(color=0x5f0aee,
        description='Server Starting (it might take a while)...')
        await ctx.send(embed=embed)
    
    # @commands.command()
    # async def start2(self, message):
    #         channel = message.channel
    #         await asyncio.sleep(.5)
    #         await channel.send('This is only useful if many people are joining the server at one time and/or the server is lagging')
    #         await asyncio.sleep(1)
    #         await channel.send('This server cannot start if another server is already started!')
    #         await asyncio.sleep(1)
    #         await channel.send('If you know there is no other server active, react to this message with 👍 within 20 seconds...')

    #         def check(reaction, user):
    #             return user == message.author and str(reaction.emoji) == '👍'

    #         try:
    #             await self.client.wait_for(self, event = 'reaction_add', timeout=20.0, check=check)
    #         except asyncio.TimeoutError:
    #             await channel.send('Reaction timed out!')
    #         else:
    #             await channel.send('Starting 2 Jigglybit server')
    #             subprocess.Popen(r'D:\server-dont-delete-ffs\creative_server\start2.bat', cwd=r'D:\server-dont-delete-ffs\creative_server', shell=True)
    #             embed=discord.Embed(title='View Map in Browser',
    #             url='http://73.49.109.86:8100/',
    #             color=0x5f0aee,
    #             description='Starting the server with 2 Jigglybits')
    #             embed.set_footer(text='Join on port 25567')
    #             await message.send(embed=embed)


def setup(bot):
    bot.add_cog(ServerCommands(bot))

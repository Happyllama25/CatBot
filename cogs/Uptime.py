import datetime, time, disnake
from disnake.ext import commands

class Uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded') 
        global startTime
        startTime = time.time()

    @commands.command()
    async def uptime(self, ctx):

        uptime = str(datetime.timedelta(seconds=int(round(time.time()-startTime))))
        embed=disnake.Embed(title="Uptime", color=0x4308db, description=uptime)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Uptime(bot))
import datetime, time, disnake
from disnake.ext import commands

class Uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.startTime = time.time()  # Store the start time as an attribute of the bot

    @commands.slash_command(name='uptime', description='Uptime of the bot')
    async def uptime(self, ctx):
        uptime = str(datetime.timedelta(seconds=int(round(time.time() - self.bot.startTime))))
        embed=disnake.Embed(title="Uptime", color=0x4308db, description=uptime)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Uptime(bot))

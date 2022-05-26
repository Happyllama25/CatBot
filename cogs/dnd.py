import disnake, random
from disnake.ext import commands


class dnd(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded - lets get rolling')

    @commands.command(aliases=["d"])
    async def roll(self, ctx, int = 6):
        await ctx.send(random.randint(1, int))

        
def setup(bot):
    bot.add_cog(dnd(bot))

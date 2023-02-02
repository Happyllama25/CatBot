import disnake, requests
from disnake.ext import commands


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        @commands.command(aliases=["recognise"])
        async def recognize(self, ctx, link):

            

    

def setup(bot):
    bot.add_cog(Music(bot))

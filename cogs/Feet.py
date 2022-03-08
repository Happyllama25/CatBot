import disnake, random
import os
from disnake.ext import commands



class Feet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded - rawr')


    

    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000) }ms")

def setup(bot):
    bot.add_cog(Feet(bot))
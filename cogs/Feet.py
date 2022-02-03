import discord, random
import os
from discord.ext import commands

images = os.path.join(os.path.dirname(__file__), "feet/")
images_list = [images + c for c in os.listdir(images)]

class Feet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded - rawr')

    # @commands.command(name='Feet')
    # async def feet(self, ctx):
    #     await ctx.send(file=discord.File(random.choice(Feetpix)))

    @commands.command(name='test')
    async def test(self, ctx: commands.Context):
        await ctx.send(file=discord.File(random.choice(images)))



    @commands.command(name = "feet", aliases=["aliase"])
    async def  feet(self, ctx:commands.Context):
        await ctx.send(file=discord.File(random.choice(images)))


def setup(bot):
    bot.add_cog(Feet(bot))
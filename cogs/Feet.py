import disnake, random
import os
from disnake.ext import commands



class Feet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded - rawr')
    
    @commands.command()
    async def feet(self, ctx):
        directory = os.path.join(os.getcwd(), "feet")
        random_image_path = os.path.join(directory, random.choice(os.listdir(directory)))
        
        await ctx.send(file=disnake.File(random_image_path, 'why_are_you_downloading_this.jpeg', spoiler=True, description='stinky floor grippers'))
        
    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000) }ms")

def setup(bot):
    bot.add_cog(Feet(bot))
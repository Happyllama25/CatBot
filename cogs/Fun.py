import aiohttp, discord
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')

    @commands.command(name='catfact', help='Sends a random CatFact.')
    async def catfact(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://catfact.ninja/fact") as response:
                fact = (await response.json())["fact"]
                length = (await response.json())["length"]
                embed = discord.Embed(title=f'Random Cat Fact Number: **{length}**', description=f'Cat Fact: {fact}', colour=0x400080)
                embed.set_footer(text="")
                await ctx.send(embed=embed)

    @commands.command(name='meow', help='Posts a random picture of a cat,')
    async def meow(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.thecatapi.com/v1/images/search") as response:
                picture = (await response.json())[0]["url"]
                embed = discord.Embed(title=f'Random Cat Picture:', colour=0x400080)
                embed.set_image(url = picture)
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
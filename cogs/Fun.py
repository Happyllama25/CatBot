import os
import subprocess
import sys
import aiohttp, disnake, asyncio
from disnake.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')

        
    @commands.command(name = "say")
    async def say(self, ctx, *, message = 'CatBot is the best'):
        await ctx.message.delete()
        await ctx.send(message)
        
    @commands.command(name='catfact', help='Sends a random CatFact.')
    async def catfact(self, ctx, n = 1):
        for i in range(n):
            async with aiohttp.ClientSession() as session:
                async with session.get("https://catfact.ninja/fact") as response:
                    fact = (await response.json())["fact"]
                    length = (await response.json())["length"]
                    embed = disnake.Embed(title=f'Random Cat Fact Number: **{length}**', description=f'Cat Fact: {fact}', colour=0x400080)
                    embed.set_footer(text="")
                    await ctx.send(embed=embed)
                    await asyncio.sleep(1)
            if n >= 6 or n <= 0:
                await ctx.send("Loop amount can't be greater than 5 or less than 0")
                break

    @commands.command(name='meow', help='Posts a random picture of a cat')
    async def meow(self, ctx, n = 1):
        for i in range(n):
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.thecatapi.com/v1/images/search") as response:
                    picture = (await response.json())[0]["url"]
                    embed = disnake.Embed(title=f'Random Cat Picture:', colour=0x400080)
                    embed.set_image(url = picture)
                    await ctx.send(embed=embed)
                    await asyncio.sleep(1)
            if n >= 6 or n <= 0:
                await ctx.send("Loop amount can't be greater than 5 or less than 0")
                break
                
    @commands.command(name='bricc', help='bricc')
    async def bricc(self, ctx, n = 1):
        for i in range(n):
            embed = disnake.Embed(title=f'bricc', colour=0x400080)
            embed.set_image(url = "https://c.tenor.com/UEYxx6a-VtgAAAAd/brick-eating.gif")
            await ctx.send(embed=embed)
            await asyncio.sleep(1)
            if n >= 6 or n <= 0:
                await ctx.send("Loop amount can't be greater than 5 or less than 0")
                break

    @commands.command(name='remind', help='Reminds you of something with time')
    async def remind(self, ctx, time, *, task):
        def convert(time):
            pos = ['s', 'm', 'h', 'd']

            time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600*24}

            unit = time[-1]

            if unit not in pos:
                return -1
            try:
                val = int(time[:-1])
            except:
                return -2
 
            return val * time_dict[unit]

        converted_time = convert(time)

        if converted_time == -1:
            await ctx.send("The time is incorrect")
            return
        
        if converted_time == -2:
            await ctx.send("Time must be an integer (numbers dum dum)")
            return
        
        await ctx.send(f"Started reminder for **{task}** and will remind in **{time}**.")

        await asyncio.sleep(converted_time)
        await ctx.send(f"{ctx.author.mention} your reminder for **{task}** has finished!")

    @commands.command()
    async def members(self, ctx):
        membersBots = ctx.guild.member_count - len([x for x in ctx.guild.members if not x.bot])
        membersUsers = len([x for x in ctx.guild.members if not x.bot])
        await ctx.send(f"Total members: {ctx.guild.member_count}\nBots: {membersBots}\nUsers: {membersUsers}")

    @commands.command()
    async def changepres(self, ctx, type, *, message):
        if type and message == None or type != 'watching' or 'listening' or 'streaming':
            await ctx.message.send(f"Possible types are: watching, streaming and listening")
            return
        typeFull = f'disnake.Activity.{type}'
        await self.bot.change_presence(activity=disnake.Activity(type=typeFull, name=message))
        await ctx.message.send(f'Activity changed to `{type} {message}`')


def setup(bot):
    bot.add_cog(Fun(bot))
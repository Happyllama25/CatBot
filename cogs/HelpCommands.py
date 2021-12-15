from discord.ext import commands
import discord


class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')

    @commands.command(name = "help", aliases=["commands"])
    async def  help(self, ctx):
        embedVar = discord.Embed(title="Help", description="List of commands:", color=0x5f0aee)
        embedVar.add_field(name="$meow", value="Sends a picture of a cute cat", inline=False)
        embedVar.add_field(name="$catfact", value="Sends a cool cat fact", inline=False)
        embedVar.add_field(name="$ip",value="Tells you the IP to join the creative server", inline=False)
        embedVar.add_field(name="$remind",value="Reminder command. seconds, minutes, hours and days are valid")
        embedVar.add_field(name="-help",value="Sill send you a DM with the music commands", inline=False)

        await ctx.send(embed=embedVar)

def setup(bot):
    bot.add_cog(HelpCommands(bot))
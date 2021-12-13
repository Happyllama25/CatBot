from discord.ext import commands
import discord


class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')

    @commands.group(name='help', invoke_without_command=True)
    async def helpcommand(self, ctx):
        await ctx.channel.send("Base help command. Accepted arguments: fun, server, music, admin")

    @helpcommand.command(name='fun')
    async def fun_subcommand(self, ctx):
        embedVar = discord.Embed(title="Fun Help", description="List of available fun commands!", color=0x5f0aee)
        embedVar.add_field(name="$meow", value="Sends a picture of a cute cat.", inline=False)
        embedVar.add_field(name="$catfact", value="Sends a cool cat fact.", inline=False)
        await ctx.send(embed=embedVar)


    @helpcommand.command(name='server')
    async def server_subcommand(self, ctx):
        embedVar = discord.Embed(title="Server Help", description="List of available server commands!", color=0x5f0aee)
        embedVar.add_field(name="$start",value="Starts the Minecraft Creative Server", inline=False)
        embedVar.add_field(name="$start2",value="Starts the Minecraft Creative Server with 2Gb of RAM", inline=False)
        embedVar.add_field(name="$startold",value="Starts the old Minecraft Creative Server", inline=False)
        await ctx.send(embed=embedVar)

    @helpcommand.command(name='music')
    async def music_subcommand(self, ctx):
        emb = discord.Embed(title="Fun Help", description="List of available fun commands!", color=0x5f0aee)
        emb.add_field(name="join",value="Joins the voice-channel you are currently in.")
        emb.add_field(name="",value="")
        await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(HelpCommands(bot))
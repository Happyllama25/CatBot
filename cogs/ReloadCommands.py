from disnake.ext import commands
import os

class ReloadCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')

    @commands.group(name = 'reload', invoke_without_command=True)
    async def reload(self, ctx):
        await ctx.send('Valid subcommands are: all, admin, fun, help, music, server and uptime')

    @reload.command(name = 'all')
    @commands.is_owner()
    async def all(self, ctx):
        await ctx.send('Reloading all commands...')
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") == True:
                commands.Bot.reload_extension(self, name={filename[:-3]})
        


    @reload.command(name = 'admin')
    async def admin(self, ctx):
        await ctx.send('Reloading admin commands...')
        commands.Bot.reload_extension(self, name='cogs.AdminCommands')

    @reload.command(name = 'fun')
    async def fun(self, ctx):
        await ctx.send('Reloading fun commands...')
        commands.Bot.reload_extension(self,"cogs.Fun")

    @reload.command(name = 'help')
    async def help(self, ctx):
        await ctx.send('Reloading help commands...')
        commands.Bot.reload_extension(self, name='cogs.HelpCommands')

    @reload.command(name = 'music')
    async def music(self, ctx):
        await ctx.send('Reloading music commands...')
        commands.Bot.reload_extension(self, name='cogs.MusicCommands')

    @reload.command(name = 'server')
    async def server(self, ctx):
        await ctx.send('Reloading server commands...')
        commands.Bot.reload_extension(self, name='cogs.ServerCommands')

    @reload.command(name = 'uptime')
    async def uptime(self, ctx):
        await ctx.send('Reloading uptime commands...')
        commands.Bot.reload_extension(self, name='cogs.Uptime')

def setup(bot):
    bot.add_cog(ReloadCommands(bot))
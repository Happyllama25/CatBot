import disnake
from disnake.ext import commands
guilds = [8888888888, 8888888888]

class Slashcommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(name='ping',
                            description='Sends bot latency',
                            guild_ids=guilds)
    async def ping(self, ctx):
        await ctx.send(content = f'Pong! {round(self.bot.latency * 1000)}ms', ephemeral = True)




def setup(bot):
    bot.add_cog(Slashcommands(bot))

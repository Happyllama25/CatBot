from discord import errors
from discord.ext import commands
import time

class CommandEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
 
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')
 
    @commands.Cog.listener()
    async def on_error(self, ctx):
        print(ctx.command.name + "has failed!")
        print(errors)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        print(ctx.command.name + " success")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f'This command is on cooldown, you can use it in {round(error.retry_after)} seconds.')
            time.sleep(3)
            await message.delete()


def setup(bot):
    bot.add_cog(CommandEvents(bot))
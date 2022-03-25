from datetime import datetime
from disnake import errors
from disnake.ext import commands
import time, disnake, os

channelID = int(os.getenv('LOGGING_CHANNEL_ID'))



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
            await message.delete(delay=3)

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        time = datetime.now().strftime('%H:%M:%S')
        embed = disnake.Embed(title="{} deleted a message".format(message.author.name),
                            description="", color=0xFF0000)
        embed.add_field(name=f"Message deleted in {message.channel}", value=message.content,
                        inline=True)
        embed.set_footer(text=f'ID: {message.id} • Time: {time}')
        channel = self.bot.get_channel(channelID)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        time = datetime.now().strftime('%H:%M:%S')
        embed = disnake.Embed(title="{} edited a message".format(before.author.name),
                          description="", color=0xFF0000)
        embed.add_field(name=before.content, value="Before the edit",
                        inline=True)
        embed.add_field(name=after.content, value="After the edit",
                        inline=True)
        embed.set_footer(text=f'ID: {after.id} • Time: {time}')
        channel = self.bot.get_channel(channelID)
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(CommandEvents(bot))
from datetime import datetime
from disnake.ext import commands
import disnake, os

channelID = int(os.getenv('LOGGING_CHANNEL_ID'))



class CommandEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
 
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')
 
    @commands.Cog.listener()
    async def on_error(self, ctx, errors):
        print(ctx.command.name + "has failed!")
        print(errors)

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        time = datetime.now().strftime('%H:%M:%S')
        msg = f"```diff\n- Message deleted by {message.author.name}\n- message.content\n+ Time: {time} ```"
        channel = self.bot.get_channel(channelID)
        await channel.send(msg)

    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        if before.author == self.bot.user or before.content == after.content:
            return

        time = datetime.now().strftime('%H:%M:%S')
        msg = f"```diff\n- Message edited by {before.author.name}\n- {before.content}\n+ {after.content}\n+ Time: {time} ```"

        channel = self.bot.get_channel(channelID)
        await channel.send(msg)


def setup(bot): 
    bot.add_cog(CommandEvents(bot))
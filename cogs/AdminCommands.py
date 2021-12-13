import discord
from discord.ext import commands


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')


    #bans a user with a reason
    @commands.command()
    @commands.has_any_role("THE E L E V A T E D ONES")
    async def ban (ctx, member:discord.User=None, reason =None):
        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot ban yourself")
            return
        if reason == None:
            reason = "For being a jerk!"
        message = f"You have been banned from {ctx.guild.name} for {reason}"
        await member.send(message)
        # await ctx.guild.ban(member, reason=reason)
        await ctx.channel.send(f"{member} is banned!")


def setup(bot):
    bot.add_cog(AdminCommands(bot))
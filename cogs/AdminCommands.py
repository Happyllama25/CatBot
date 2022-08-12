import disnake, os
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv('config.env')

adminrole = int(os.getenv('ADMIN_ROLE_ID'))

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')


    #bans a user with a reason
    @commands.command()
    @commands.has_role(adminrole)
    async def ban (self, ctx, member:disnake.User=None, reason =None):
        if member == None or member == ctx.message.author:
            message = await ctx.channel.send("Specify user")
            await message.delete(delay=3)
            return
        if reason == None:
            reason = "not having enough skill"
        message = f"ur banned from {ctx.guild.name} for {reason}\n\nlol fkin noob"
        await member.send(message)
        await ctx.guild.ban(member, reason=reason)
        await ctx.channel.send(f"{member} has a severe lack of skill")

    #kicks a user with a reason
    @commands.command()
    @commands.has_role(adminrole)
    async def kick(self, ctx, member:disnake.User=None, reason=None):
        if member == None or member == ctx.message.author:
            message = await ctx.channel.send("Specify user")
            await message.delete(delay=3)
            return
        if reason == None:
            reason = "not having enough skill"
        message = f"u were kicked from {ctx.guild.name} for {reason}\n\nlol noob"
        await member.send(message)
        await ctx.guild.kick(member, reason=reason)
        await ctx.channel.send(f"{member} has a slightly above average lack of skill")
        
    @commands.command()
    @commands.has_role(adminrole)
    async def unban(self, ctx, member:disnake.User=None, reason=None):
        if member == None:
            message = await ctx.channel.send("Specify member")
            await message.delete(delay=3)
        if reason == None:
            reason = "has enough skill"
        await ctx.guild.unban(member, reason=reason)
        invite = ctx.guild.create_invite(max_uses=1, max_age=28800) #8 hours
        await member.send(f'okay you have enough skill pls come back uwu\n\n{invite}')
      
    @commands.command(aliases=['purge', 'delete', 'del']) #Clear Command
    @commands.has_permissions(manage_messages = True)
    async def clear(ctx, amount=2):
        await ctx.message.delete()
        if amount >=15:
            await ctx.channel.purge(limit = 15)
            return
        else:
            await ctx.channel.purge(limit = amount)
        #Add limit to prevent too many deletes
    

def setup(bot):
    bot.add_cog(AdminCommands(bot))
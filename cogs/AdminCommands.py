import disnake, os
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv('config.env')

adminrole = int(os.getenv('ADMIN_ROLE_ID'))

print(adminrole)

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx):
        try:
            embed=disnake.Embed(title="⚠️ Server lockdown ⚠️", color=0xff0400)
            embed.add_field(name="Please wait until lockdown is lifted", value='the roomba is observing')
            for channel in ctx.guild.channels:
                channel.set_permissions(target=ctx.guild.default_role, send_messages=False)
            await ctx.send(embed=embed)
        except Exception as error:
            await ctx.send(f'Failed: {error}')


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def releaselockdown(self, ctx):
        try:
            embed=disnake.Embed(title="Channel unlocked", color=0xff0400)
            embed.add_field(name="Roomba deployed for cleanup", value='brrrmm')
            for channel in self.guild.channels:
                channel.set_permissions(self.guild.default_role, overwrite=None)
            await ctx.send(embed=embed)
        except Exception as error:
            await ctx.send(f'Failed: {error}')
            
      

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
    async def kick(self, ctx, member:disnake.User=None, reason='not having enough skill'):
        if member == None or member == ctx.message.author:
            message = await ctx.channel.send("Specify user")
            await message.delete(delay=3)
            await ctx.message.delete(delay=3)
            return
        message = f"u were kicked from {ctx.guild.name} for {reason}\n\nuwu rawr OwO"
        await member.send(message)
        await ctx.guild.kick(member, reason=reason)
        await ctx.channel.send(f"{member} has a slightly above average lack of skill")
        
    @commands.command()
    @commands.has_role(adminrole)
    async def unban(self, ctx, member:disnake.User=None, reason=None):
        if member == None:
            message = await ctx.channel.send("Specify member")
            await message.delete(delay=3)
            await ctx.message.delete(delay=3)
            return
        if reason == None:
            reason = "has enough skill"
        try: 
            await ctx.guild.unban(user=member, reason=reason)
            await ctx.message.send(f'Unbanned {member}')
        except:
            await ctx.message.send(f'Could not unban {member} (Needs user ID)')
      
    @commands.command(aliases=['purge', 'delete', 'del']) #Clear Command
    @commands.has_permissions(manage_messages = True)
    async def clear(ctx, amount=5):
        await ctx.message.delete()
        if amount >=31:
            await ctx.channel.purge(limit = 30)
            return
        else:
            await ctx.channel.purge(limit = amount)
        #Add limit to prevent too many deletes
    

def setup(bot):
    bot.add_cog(AdminCommands(bot))
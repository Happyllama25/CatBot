import disnake, os
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv('config.env')

#adminrole = int(os.getenv('ADMIN_ROLE_ID'))

#print(adminrole)

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')

    #bans a user with a reason 
    @commands.slash_command(name='ban', description='Bans a user')
    @commands.default_member_permissions(manage_guild=True, moderate_members=True)
    async def ban(self, ctx, member:disnake.User, reason:str = 'the silly is unreal'):
        try:
            message = f"Banned from {ctx.guild.name} for {reason}"
            await member.send(message)
            await ctx.guild.ban(member, reason=reason)
            await ctx.send(f"{member} has a severe lack of skill")
        except Exception as error:
            await ctx.send(f'Error:\n{error}')
    
    @commands.slash_command(name='ban_role', description='Bans all members of a role')
    @commands.default_member_permissions(manage_guild=True, moderate_members=True)
    async def ban_role(self, ctx, role: disnake.Role, reason: str = 'the silly is unreal'):
        ctx.response.defer()
        try:
            members = role.members
            if len(members) == 0:
                return await ctx.edit_original_response("Role has no members.")
            for member in members:
                message = f"Banned from {ctx.guild.name} for {reason}"
                await member.send(message)
                await member.ban(reason=reason)
            await ctx.edit_original_response(f"{len(members)} member(s) from {role.mention} have been banned.")
        except Exception as error:
            await ctx.edit_original_response(f"An error occurred while trying to ban members and has been printed to the log.\n\n{error}")
            print(error)

    @commands.slash_command(name='kick', description='Kicks a user')
    @commands.default_member_permissions(manage_guild=True, moderate_members=True)
    async def kick(self, ctx, member:disnake.User, reason='slightly silly'):
        try:
            message = f"u were kicked from {ctx.guild.name} for {reason}"
            await member.send(message)
            await ctx.guild.kick(member, reason=reason)
            await ctx.send(f"{member} has a slightly above average lack of skill")
        except Exception as error:
            await ctx.send(f'Error:\n{error}')

    @commands.slash_command(name='purge',description='Purges messages in a channel')
    @commands.default_member_permissions(manage_messages=True)
    async def purge(self, ctx, amount:int = commands.Param(default=1,gt=0,lt=30)):
        await ctx.channel.purge(limit = amount)
        await ctx.send(f'Purged {amount} messages mrrow!')


def setup(bot):
    bot.add_cog(AdminCommands(bot))
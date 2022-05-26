import discord
from discord.ext import commands


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')


    @commands.command(aliases=['purge']) #Clear Command
    @commands.has_permissions(manage_messages = True)
    async def clear(ctx,amount=2):
        await ctx.channel.purge(limit = amount)

    @commands.command() #Kick Command
    @commands.has_permissions(kick_members = True)
    async def kick(ctx,member : discord.Member,*,reason= "No reason provided"):
        try:
            await member.send("You have been kicked from Happyllama25's Twitch Discord for: " + reason)
            await member.kick(reason=reason)
        except:
            await member.kick(reason=reason)
        else:
            ctx.send("An error occured and the member was not kicked.")


    @commands.command() #Ban Command
    @commands.has_permissions(ban_members = True)
    async def ban(ctx,member : discord.Member,*,reason= "No reason provided"):
        try:
            await member.send("You have been banned from " + ctx.guild.name + " for: " + reason)
            await member.ban(reason=reason)
        except:
            await member.ban(reason=reason)
        else:
            await ctx.send("An error occured and the member was not banned.")


    @commands.command() #Unban Command
    @commands.has_permissions(ban_members = True)
    async def unban(ctx,*,member):
        banned_users = await ctx.guild.bans()
        member_name, member_disc = member.split('#')

        for banned_entry in banned_users:
            user = banned_entry.user

            if(user.name, user.discriminator)==(member_name,member_disc):

                await ctx.guild.unban(user)
                await ctx.send(member_name + " has been unbanned.")
                return

        await ctx.send(member + " was not found...")
    

    @commands.command(aliases=['m']) #Mute Command
    @commands.has_permissions(kick_members = True)
    async def mute(ctx,member : discord.Member):

        muted_role = ctx.guild.get_role(718100476125642843)
        await member.add_roles(muted_role)
        await ctx.send(member.mention + " has been muted")



    @commands.command() #Unmute Command
    @commands.has_permissions(kick_members = True)
    async def unmute(ctx,member : discord.Member):
        muted_role = ctx.guild.get_role(718100476125642843)

        await member.remove_roles(muted_role)
        await ctx.send(member.mention + " has been unmuted")




def setup(bot):
    bot.add_cog(AdminCommands(bot))
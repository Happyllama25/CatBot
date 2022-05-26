import disnake
from disnake.ext import commands


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} has been loaded')


    #ban user wiht a reason
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member : disnake.Member = None, *, reason= "not having enough skill"):
        if member == None:
            message = await ctx.channel.send("Specify user")
            await message.delete(delay=3)
            return
        else:
            try:
                await member.send(f"ur banned from {ctx.guild.name} for {reason}\n\nlol noob")
                await member.ban(reason=reason)
                await ctx.channel.send(f"{member} has a severe lack of skill")
            except:
                await member.ban(reason=reason)
                await ctx.channel.send(f"{member} has a severe lack of skill")
            else:
                await ctx.send("uhh smthn hapen no worky :(")


        # if member == None or member == ctx.message.author:
        #     message = await ctx.channel.send("Specify user")
        #     await message.delete(delay=3)
        #     return
        # if reason == None:
        #     reason = "not having enough skill"
        # message = f"ur banned from {ctx.guild.name} for {reason}\n\nlol noob"
        # await member.send(message)
        # await ctx.guild.ban(member, reason=reason)
        # await ctx.channel.send(f"{member} has a severe lack of skill")

    #kicks a user with a reasonnang0'aigreiohgpuerip
    @commands.command()
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member:disnake.User=None, *, reason="not having enough skill"):
        if member == None:
            message = await ctx.channel.send("Specify user")
            await message.delete(delay=3)
            return
        else:
            try:
                await member.send(f"u were kicked from {ctx.guild.name} for {reason}\n\nlol noob")
                await member.kick(reason=reason)
                await ctx.channel.send(f"{member} has a slightly below average lack of skill")
            except:
                await member.kick(reason=reason)
                await ctx.channel.send(f"{member} has a slightly below average lack of skill")
            else:
                ctx.send("uh oh stinky poop ahaha poopy stimky (eror ocurdd no worki)")

    @commands.command() #Unban Command
    @commands.has_permissions(ban_members = True)
    async def unban(ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_disc = member.split('#')

        for banned_entry in banned_users:
            user = banned_entry.user

            if(user.name, user.discriminator)==(member_name, member_disc):

                await ctx.guild.unban(user)
                await ctx.send(f"{member_name} wuz unbanned and invited bakc")
                invite = ctx.guild.create_invite(max_uses=1, max_age=28800) #8 hours
                await member.send(f'okay you have enough skill pls come back uwu\n\n{invite}')
                return

        await ctx.send(f"{member} was not found")


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

    # @commands.command()
    # @commands.has_role(adminrole)
    # async def unban(self, ctx, member:disnake.User=None, reason=None):
    #     if member == None:
    #         message = await ctx.channel.send("Specify member")
    #         await message.delete(delay=3)
    #     if reason == None:
    #         reason = "has enough skill"
    #     await ctx.guild.unban(member, reason=reason)
    #     invite = ctx.guild.create_invite(max_uses=1, max_age=28800) #8 hours
    #     await member.send(f'okay you have enough skill pls come back uwu\n\n{invite}')


def setup(bot):
    bot.add_cog(AdminCommands(bot))
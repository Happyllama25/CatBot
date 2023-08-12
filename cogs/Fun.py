
import aiohttp, disnake, asyncio, requests, os, random
from disnake.ext import commands
from enum import Enum
from typing import Optional

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "say")
    @commands.is_owner()
    async def say(self, ctx, *, message = 'CatBot is the best'):
        await ctx.message.delete()
        await ctx.send(message)

    @commands.slash_command(name='catfact', description='Sends a random CatFact.')
    async def catfact(self, ctx, number:int = commands.Param(default=1,gt=0,lt=6)):
        for i in range(number):
            request = requests.get("https://catfact.ninja/fact")
            fact = request.json()["fact"]
            number = request.json()["length"]
            embed = disnake.Embed(title=f'Random Cat Fact Number: **{number}**', description=f'Cat Fact: {fact}', colour=0x400080)
            
            await ctx.send(embed=embed)
            await asyncio.sleep(1)

    @commands.slash_command(name='meow', description='Posts a random picture of a cat')
    async def meow(self, ctx, number:int = commands.Param(default=1,gt=0,lt=6)):
        for int in range(number):
            request = requests.get("https://api.thecatapi.com/v1/images/search")
            url = request.json()[0]["url"]
            embed = disnake.Embed(title='Random Cat Picture:', colour=0x400080)
            embed.set_image(url = url)
            await ctx.send(embed=embed)
            await asyncio.sleep(1)

    @commands.slash_command(name='insult', description='Sends a random insult optionally directed to someone')
    async def insult(self, ctx, user: Optional[disnake.User] = None):
        if user is None:
            url = "https://insult.mattbas.org/api/insult"
            response = requests.get(url=url, timeout=5).text
        else:
            url = f"https://insult.mattbas.org/api/insult?who={user.display_name}"
            response = requests.get(url=url, timeout=5).text
            response = response.replace(user.display_name, user.mention)
        await ctx.send(response.capitalize())

    @commands.slash_command(name='bricc',description="bricc", help='bricc')
    async def bricc(self, ctx, amount:int = commands.Param(default=1,gt=0,lt=6)):
        for i in range(amount):
            embed = disnake.Embed(title='bricc', colour=0x400080)
            embed.set_image(url = "https://c.tenor.com/UEYxx6a-VtgAAAAd/brick-eating.gif")
            await ctx.send(embed=embed)
            await asyncio.sleep(0.5)

    @commands.command(name='remind', help='Reminds you of something with time')
    async def remind(self, ctx, time, *, task):
        def convert(time):
            pos = ['s', 'm', 'h', 'd']
            time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600*24}
            unit = time[-1]

            if unit not in pos:
                return -1
            try:
                val = int(time[:-1])
            except:
                return -2
            return val * time_dict[unit]
        converted_time = convert(time)
        if converted_time == -1:
            await ctx.send("The time is incorrect")
            return
        if converted_time == -2:
            await ctx.send("Time must be an integer (numbers dum dum)")
            return
        
        await ctx.send(f"Started reminder for **{task}** and will remind in **{time}**.")
        await asyncio.sleep(converted_time)
        await ctx.send(f"{ctx.author.mention} your reminder for **{task}** has finished!")

    @commands.slash_command(name='heyguys' ,description="hey guys")
    async def heyguys(self, ctx):
        await ctx.send("Hey guys, did you know that in terms of male human and female Pokémon breeding, Vaporeon is the most compatible Pokémon for humans? Not only are they in the field egg group, which is mostly comprised of mammals, Vaporeon are an average of 3''03' tall and 63.9 pounds, this means they're large enough to be able handle human dicks, and with their impressive Base Stats for HP and access to Acid Armor, you can be rough with one. Due to their mostly water based biology, there's no doubt in my mind that an aroused Vaporeon would be incredibly wet, so wet that you could easily have sex with one for hours without getting sore. They can also learn the moves Attract, Baby-Doll Eyes, Captivate, Charm, and Tail Whip, along with not having fur to hide nipples, so it'd be incredibly easy for one to get you in the mood. With their abilities Water Absorb and Hydration, they can easily recover from fatigue with enough water. No other Pokémon comes close to this level of compatibility. Also, fun fact, if you pull out enough, you can make your Vaporeon turn white. Vaporeon is literally built for human dick. Ungodly defense stat+high HP pool+Acid Armor means it can take cock all day, all shapes and sizes and still come for more")

    @commands.slash_command(name="members", description="Displays server statistics")
    async def members(self, ctx):
        guild = ctx.guild

        # Gathering statistics
        online_members = sum(1 for member in guild.members if member.status != disnake.Status.offline)
        text_channels = len([channel for channel in guild.channels if isinstance(channel, disnake.TextChannel)])
        voice_channels = len([channel for channel in guild.channels if isinstance(channel, disnake.VoiceChannel)])
        role_count = len(guild.roles)
        emoji_count = len(guild.emojis)
        bots = sum(1 for member in guild.members if member.bot)

        # Creating an embed with the statistics
        embed = disnake.Embed(title=f"Stats for {guild.name}", color=disnake.Color.blue())
        embed.add_field(name="Server Creation Date", value=guild.created_at.strftime('%Y-%m-%d %H:%M:%S'))
        embed.add_field(name="Member Count", value=str(guild.member_count))
        embed.add_field(name="Online Members", value=str(online_members))
        embed.add_field(name="Total Channels", value=str(text_channels + voice_channels))
        embed.add_field(name="Text Channels", value=str(text_channels))
        embed.add_field(name="Voice Channels", value=str(voice_channels))
        embed.add_field(name="Role Count", value=str(role_count))
        embed.add_field(name="Emoji Count", value=str(emoji_count))
        embed.add_field(name="Verification Level", value=str(guild.verification_level))
        embed.add_field(name="Boost Level", value=str(guild.premium_tier))
        embed.add_field(name="Number of Boosts", value=str(guild.premium_subscription_count))
        embed.add_field(name="Bots", value=str(bots))

        await ctx.send(embed=embed)
    @commands.slash_command(name = 'xkcd', description = 'Daily comics from xkcd')
    async def xkcd(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://xkcd.com/info.0.json") as response:
                comic = (await response.json())["img"]
                title = (await response.json())["title"]
                alt = (await response.json())["alt"]
                number = (await response.json())["num"]
                embed = disnake.Embed(title=title, colour=0x400080)
                embed.set_image(url = comic)
                embed.set_footer(text=f'{alt} - #{number}')
                await ctx.response.send_message(embed=embed)

    @commands.slash_command(name='feet', description='random stinky pic of somones feet, or deposit anonymously')
    async def feet(self, ctx, deposit: Optional[disnake.Attachment] = None):
        if deposit is None:
            directory = os.path.join(os.getcwd(), "feet")
            random_image_path = os.path.join(directory, random.choice(os.listdir(directory)))
            
            await ctx.send(file=disnake.File(random_image_path, 'why_are_you_downloading_this.jpeg', spoiler=True, description='shtinky floor grippers'))
            return
        else:
            try:
                filename = f'./feet/{deposit.filename}'
                await deposit.save(fp=filename)
                await ctx.send(f'your donation of `{deposit.filename}` is ***very*** appreciated', ephemeral=True)
                print('FOOT DEPOSIT SUCCESSFUL')
            except Exception as error:
                await ctx.send(f'Saving failed - Ping Happyllama25 with a screenshot of this error\n\n{error}', ephemeral=True)

def setup(bot):
    bot.add_cog(Fun(bot))
import os, asyncio
from dotenv import load_dotenv
load_dotenv('.env')
import disnake
from disnake.ext import commands


TOKEN = os.getenv('DIS_TOKEN')
extensions = ['cogs.Gpt', 'cogs.Fun', 'cogs.Uptime', 'cogs.Feet', 'cogs.Panel', 'cogs.AdminCommands', 'cogs.ReloadCommands']


watchingStatus = [
    "you in your sleep",
    "the ELEVATED ONES",
    "#gaming",
    "Happyllama25 melt",
	"you sleep",
	"over you",
	"your mom"
    ]

# , 'cogs.HelpCommands', 'cogs.ServerCommands'
bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'), intents=disnake.Intents.all(), reload=True, strip_after_prefix=True)


# # Define the guild ID and user ID to check
# guild_id = 883224856047525888
# user_id = 523572483014656001


@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name='Bot Started!'))
    print('Ready!')
    # Fetch the guild object using the guild ID
    # guild = bot.get_guild(guild_id)
    # if guild is None:
    #     print('Guild not found')
    #     return
    # # Fetch the member object using the user ID
    # member = await guild.fetch_member(user_id)
    # if member is None:
    #     print('Member not found')
    #     return
    # # Call the game_detect function to check if the member is playing a game
    # await bot.loop.create_task(game_detect(member))
    await bot.loop.create_task(status_cycle())
    
# # Define the game_detect function
# async def game_detect(member: disnake.Member) -> None:
#     print('running')
#     while True:
#         game = None
#         for activity in member.activities:
#             if isinstance(activity, disnake.Game):
#                 game = activity
#                 print(f'Game detected: {game}')
#         if not member.activities:
#             print('Member is not playing a game.')
#         elif game is None:
#             print('Member is playing an activity other than a game.')
#         elif str(member.id) != str(user_id):
#             print(f'Member ID ({member.id}) does not match the user ID ({user_id}).')
#         else:
#             print('Member is playing a game and ID matches.')
#             await member.send('https://tenor.com/view/bar-rescue-jon-taffer-go-to-fucking-work-go-to-work-pissed-gif-5085004')
#         print('reached end')
#         await asyncio.sleep(5)


async def status_cycle():
    for status in watchingStatus:
        await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name=status))
        await asyncio.sleep(69)


@bot.listen("on_message")
async def on_message(message):
    if message.author == bot.user:
        return
    if 'good catbot' in message.content:
        print('Keyword found in message')
        embed = disnake.Embed(title='😺', colour=0x400080)
        embed.set_image(url = 'https://c.tenor.com/ECAwQcWmgO4AAAAd/kitty-review.gif')
        await message.channel.send(embed=embed)
    if 'https://tenor.com/view/furry-tf2-stfu-sussy-gif-21878916' in message.content:
        print('Keyword found in message, deploying the fluff')
        await message.channel.send('https://tenor.com/view/shut-up-shut-up-normie-normie-dance-gif-16989611')
    if 'smart pistol' in message.content:
        await message.channel.send('smart pistol gay-o-meter:\n🟢🟢🟡🟡🔴🔴\n100% - very gay')
    if 'fuck me' in message.content:
        await message.channel.send('ok 😎')
    if 'bad catbot' in message.content:
        await message.channel.send('https://cdn.discordapp.com/attachments/858603126192865290/958530312000929792/unknown.png?size=4096')



for ext in extensions:
    bot.load_extension(ext)


try:
    bot.run(TOKEN)

except Exception as error:
    #print(type(TOKEN))
    #print(TOKEN)
    print(f'Failed to start. \n\nInfo: {error}')
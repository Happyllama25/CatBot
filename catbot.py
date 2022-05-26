import os, random
from dotenv import load_dotenv
load_dotenv('config.env')
import disnake
from disnake.ext import commands, tasks


TOKEN = os.getenv('DISCORD_TOKEN')
enabled = ['Fun', 'CommandEvents', 'Uptime', 'Feet', 'Panel', 'SlashCommands', 'AdminCommands', 'dnd']

# initializing append_str
append_str = 'cogs.'
  
# Append suffix / prefix to strings in list
extensions = [append_str + sub for sub in enabled]

watchingStatus = [
    "you in your sleep", 
    "the ELEVATED ONES",
    "#gaming", 
    "Happyllama25 melt",
	"you sleep",
	"over you",
	"your mom"
]

playingStatus = [
    "",
    ""
]

# , 'cogs.HelpCommands', 'cogs.ServerCommands'
bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'), intents=disnake.Intents.all(), reload=True, strip_after_prefix=True)
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name='Bot Started!'))
    print('Ready!')
    print('---------------------------------------')

# @tasks.loop()
# async def status_task():
#     await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name='Bot Started!'))


# from discord.ext import commands, tasks
# import asyncio

# # Your code here

# @tasks.loop(seconds=600)
# async def status_change():
#     statusNum = random.randint(0, 10)
#     await bot.change_presence(status=disnake.Status.online, activity=disnake.Activity(type=disnake.ActivityType.watching, name=watchingStatus[statusNum]))





@bot.listen("on_message")
async def on_message(message):
    if message.author == bot.user:
        return
    if 'good catbot' in message.content:
        print('Keyword found in message')
        embed = disnake.Embed(title=f'😺', colour=0x400080)
        embed.set_image(url = 'https://c.tenor.com/ECAwQcWmgO4AAAAd/kitty-review.gif')
        await message.channel.send(embed=embed)
    if 'https://tenor.com/view/furry-tf2-stfu-sussy-gif-21878916' in message.content:
        print('Keyword found in message')
        await message.channel.send('https://tenor.com/view/shut-up-shut-up-normie-normie-dance-gif-16989611')
    if 'smart pistol' in message.content:
        await message.channel.send(f'smart pistol gay-o-meter:\n🟢🟢🟡🟡🔴🔴\n100% - very gay')



for ext in extensions:
  bot.load_extension(ext)


try: 
    bot.run(TOKEN)

except Exception as error:
    print(f'Failed to start. \n\nInfo: {error}')
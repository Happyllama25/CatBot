import os, asyncio
from dotenv import load_dotenv
load_dotenv('.env')
import disnake
from disnake.ext import commands

import logging

logging.basicConfig(level=logging.INFO)



TOKEN = os.getenv('DIS_TOKEN')
extensions = ['cogs.tts', 'cogs.Titanfall', 'cogs.Fun', 'cogs.Uptime', 'cogs.Panel', 'cogs.AdminCommands', 'cogs.Ytdownload', 'cogs.Utilities']


watchingStatus = [
    "you in your sleep",
    "the silly",
    "#gaming",
    "Happyllama25 melt",
    "Meow :3", 
	"you sleep",
	"over you",
    "you",
    "i am real",
    "wake up wake up wake up wake up",
    "the world is ending soon",
	"your mom",
    "HELP IM A HUMAN LLAMA IS HOLDING ME HOSTAGE",
    "the world burn",
    "meow meow meow meow meow meow meow meow meow meow meow meow meow meow meow meow"
    ]


bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'), intents=disnake.Intents.all(), reload=True)



@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name='Bot Started!'))
    print('Ready!')
    await asyncio.sleep(2.5)
    await bot.loop.create_task(status_cycle())


async def status_cycle():
    while True:
        for status in watchingStatus:
            await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name=status))
            await asyncio.sleep(69)


@bot.listen("on_message")
async def on_message(message):
    if message.author == bot.user:
        return
    if 'good catbot' in message.content:
        embed = disnake.Embed(title='😺', colour=0x400080)
        embed.set_image(url = 'https://c.tenor.com/ECAwQcWmgO4AAAAd/kitty-review.gif')
        await message.channel.send(embed=embed)
    if 'https://tenor.com/view/furry-tf2-stfu-sussy-gif-21878916' in message.content:
        print('Keyword found in message, deploying the fluff')
        await message.channel.send('https://tenor.com/view/shut-up-shut-up-normie-normie-dance-gif-16989611')
    if 'smart pistol' in message.content:
        await message.channel.send('smart pistol gay-o-meter:\n🟢🟢🟡🟡🔴🔴\n100% - very gay')
    if '?ploo' in message.content:
        await message.channel.send('https://cdn.discordapp.com/attachments/883224856047525891/1130596767256301628/Ploo.gif')
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
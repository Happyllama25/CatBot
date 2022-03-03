import os
from dotenv import load_dotenv
load_dotenv('config.env')
import disnake
from disnake.ext import commands


TOKEN = os.getenv('DISCORD_TOKEN')
extensions = ['cogs.Fun', 'cogs.CommandEvents', 'cogs.Uptime', 'cogs.Feet', 'cogs.Panel']

# , 'cogs.HelpCommands', 'cogs.ServerCommands'
bot = commands.Bot(command_prefix='$', intents=disnake.Intents.all())
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name='fabian fucking die'))
    print('Ready!')



@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if 'good catbot' in message.content:
        print('Keyword found in message')
        embed = disnake.Embed(title=f'😺', colour=0x400080)
        embed.set_image(url = 'https://c.tenor.com/ECAwQcWmgO4AAAAd/kitty-review.gif')
        await message.channel.send(embed=embed)



for ext in extensions:
  bot.load_extension(ext)

bot.run(TOKEN)

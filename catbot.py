import os
from dotenv import load_dotenv
load_dotenv('config.env')
import disnake
from disnake.ext import commands


TOKEN = os.getenv('DISCORD_TOKEN')
extensions = ['cogs.Fun', 'cogs.CommandEvents', 'cogs.Uptime', 'cogs.Feet', 'cogs.Panel', 'cogs.SlashCommands']

# , 'cogs.HelpCommands', 'cogs.ServerCommands'
bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'), intents=disnake.Intents.all())
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name='fabian fucking die'))
    print('Ready!')


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



for ext in extensions:
  bot.load_extension(ext)



try: 
    bot.run(TOKEN)

except Exception as error:
    print(f'Failed to start. \n\nInfo: {error}')
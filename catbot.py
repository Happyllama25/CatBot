import os
from dotenv import load_dotenv
load_dotenv('config.env')
import discord
from discord.ext import commands


TOKEN = os.getenv('DISCORD_TOKEN')
extensions = ['cogs.Fun', 'cogs.CommandEvents', 'cogs.HelpCommands', 'cogs.ServerCommands', 'cogs.Uptime', 'cogs.Feet']

bot = commands.Bot(command_prefix='$')
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='you sleep'))
    print('Ready!')

@bot.event
async def on_message(ctx):
    if 'good catbot' in ctx.content:
        print('Keyword found in message')
        embed = discord.Embed(title=f'😺', colour=0x400080)
        embed.set_image(url = 'https://tenor.com/view/kitty-review-kittyreview-cat-squishy-gif-21044823')
        await ctx.send(embed=embed)

if __name__ == '__main__':
  for ext in extensions:
    bot.load_extension(ext)

bot.run(TOKEN)

import os
from dotenv import load_dotenv
load_dotenv('token.env')
import discord
from discord.ext import commands


TOKEN = os.getenv('DISCORD_TOKEN')
extensions = ['cogs.ReloadCommands', 'cogs.Fun', 'cogs.CommandEvents', 'cogs.HelpCommands', 'cogs.ServerCommands', 'cogs.Uptime']

bot = commands.Bot(command_prefix='$')
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='you sleep'))
    print('Ready!')

if __name__ == '__main__':
  for ext in extensions:
    bot.load_extension(ext)

bot.run(TOKEN)

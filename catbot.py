import os
from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import commands


token = os.getenv("discord_token")
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

bot.run('NjExMzAzNzY4NzgwMzA4NDgx.XVR2_w.40jQKeb7V2Bg71daPl_g21z8-mo')

from cgi import test
import discord
import requests, os
from dotenv import load_dotenv
load_dotenv('config.env')
from discord.ext import commands

API_KEY = os.getenv('API_KEY')





class Panel(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} Panel has loaded mr furry')

    @commands.command(name = "servers",
                    usage="<usage>",
                    description = "description")
    async def servers(self, ctx):
        await ctx.send('Requesting data...')

        url = 'https://panel.happyllama25.net/api/client'
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Accept": "application/json"
        }

        data = requests.request('GET', url, headers=headers).json()
        server_names = []
        server_identifiers = []

        for server in data['data']:

            server_names.append(server['attributes'] ['name'])

        for server in data['data']:

            server_identifiers.append(server['attributes'] ['identifier'])
        authorfoot = str(ctx.author) + f" ⚫ response time: " + f"ZEXOOO"
        embed=discord.Embed(title="Available Servers", color=0x00ffff)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.add_field(name="Name", value='\n'.join(server_names), inline=True)
        embed.add_field(name="Identifier", value='\n'.join(server_identifiers), inline=True)
        embed.set_footer(text=authorfoot)
        await ctx.send(embed=embed)
        server_names.clear()
        server_identifiers.clear()

    @commands.command(name = "start")
    async def start(self, ctx, id = 'null'):
        if id == 'null':
            await ctx.send("Please provide the identifier")
        else:
            await ctx.send("Querying data...")
            #Query for resources API (status, uptime, memory usage, etc)
            url = f'https://panel.happyllama25.net/api/client/servers/{id}/resources'
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Accept": "application/json"
            }

            dataresources = requests.request('GET', url, headers=headers).json()

            server_status = dataresources['attributes']['current_state']
            
            memory_unmathed = dataresources['attributes']['resources']['memory_bytes']

            memory = round(memory_unmathed / 1000000000, 2)

            await ctx.send(server_status)
            await ctx.send(str(memory) + ' GB')


            #Query for name
            url_name = f'https://panel.happyllama25.net/api/client/servers/{id}'

            dataname = requests.request('GET', url_name, headers=headers).json()
            
            name = dataname['attributes']['name']
            await ctx.send(name)
            for server in dataname['attributes']['relationships']['allocations']['data']:

                allocation = server['attributes']['ip_alias']

            for server in dataname['attributes']['relationships']['allocations']['data']:

                port = server['attributes']['port']

            await ctx.send(port)
            await ctx.send(allocation)

            
            await ctx.send(allocation + ':' + str(port))




def setup(bot:commands.Bot):
    bot.add_cog(Panel(bot))

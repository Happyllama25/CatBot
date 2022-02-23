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

        data = requests.get(url, headers=headers).json()
        server_names = []
        server_identifiers = []
        time = round(data.elapsed.microseconds / 1000)

        for server in data['data']:

            server_names.append(server['attributes'] ['name'])

        for server in data['data']:

            server_identifiers.append(server['attributes'] ['identifier'])
        embed=discord.Embed(title="Available Servers", color=0x00ffff)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.add_field(name="Name", value='\n'.join(server_names), inline=True)
        embed.add_field(name="Identifier", value='\n'.join(server_identifiers), inline=True)
        embed.set_footer(text=str(ctx.author) + f" ⚫ response time: " + str(time))
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

            dataresources = requests.get(url, headers=headers).json()

            server_status = dataresources['attributes']['current_state']
            
            memory_unmathed = dataresources['attributes']['resources']['memory_bytes']

            cpu_raw = dataresources['attributes']['resources']['cpu_absolute']

            cpu_usage = round(cpu_raw, 2)

            memory = round(memory_unmathed / 1000000000, 2)

            timeresource = round(dataresources.elapsed.microseconds / 1000)
            timename = round(dataname.elapsed.microseconds / 1000)
            time = timeresource + timename / 2
            
            statusresource = dataresources.status_code
            statusname = dataname.status_code
            statuscode = "resource: " + str(statusresource) + " name: " + str(statusname)
            await ctx.send(server_status)
            await ctx.send(str(memory) + ' GB')


            #Query for name, allocation, port
            url_name = f'https://panel.happyllama25.net/api/client/servers/{id}'

            dataname = requests.get(url_name, headers=headers).json()
            
            name = dataname['attributes']['name']
            await ctx.send(name)
            for server in dataname['attributes']['relationships']['allocations']['data']:

                allocation = server['attributes']['ip_alias']

            for server in dataname['attributes']['relationships']['allocations']['data']:

                port = server['attributes']['port']


            await ctx.send(server_status)
            await ctx.send(str(memory) + ' GB')
            await ctx.send(str(cpu_usage) + "%")
            await ctx.send(allocation + ':' + str(port))

            if server_status == "running":
                embed=discord.Embed(title="Server Status", color=0x00ffff)
                embed.add_field(name="Identifier", value=id, inline=True)
                embed.add_field(name="Status", value=server_status.capitalize(), inline=True)
                embed.add_field(name="", value="greencircle", inline=True) # Emoji line
                embed.add_field(name="Memory Usage", value=str(memory) + ' GB', inline=False)
                embed.add_field(name="CPU Usage", value=str(cpu_usage) + '%', inline=True)
                embed.add_field(name="IP:PORT", value=allocation + ':' + str(port), inline=True)
                embed.set_footer(text=str(ctx.author) + f" ⚫ response time: " + str(time))
                await ctx.send(embed=embed)
                # ADD REACTIONS TO START STOP AND RESTART





            elif server_status == "offline":
                await ctx.send('offline')
                embed=discord.Embed(title="Server Status", color=0x00ffff)
                embed.add_field(name="Identifier", value=id, inline=True)
                embed.add_field(name="Status", value=server_status.capitalize(), inline=True)
                embed.add_field(name="", value="redcircle", inline=True) # Emoji line
                embed.set_footer(text=str(ctx.author) + f" ⚫ response time: " + str(time))
                await ctx.send(embed=embed)
                # ADD REACTIONS TO START STOP AND RESTART



            elif server_status == "starting":
                await ctx.send('starting')
                embed=discord.Embed(title="Server Status", color=0x00ffff)
                embed.add_field(name="Identifier", value=id, inline=True)
                embed.add_field(name="Status", value=server_status.capitalize(), inline=True)
                embed.add_field(name="", value="yellowcircle", inline=True) # Emoji line
                embed.add_field(name="Memory Usage", value=str(memory) + ' GB', inline=False)
                embed.add_field(name="CPU Usage", value=str(cpu_usage) + '%', inline=True)
                embed.add_field(name="IP:PORT", value=allocation + ':' + str(port), inline=True)
                embed.set_footer(text=str(ctx.author) + f" ⚫ response time: " + str(time))
                await ctx.send(embed=embed)
                # ADD REACTIONS TO START STOP AND RESTART



            else:
                await ctx.send(statuscode)
                await ctx.send('Time resource request:' + str(timeresource))
                await ctx.send('Time name request:' + str(timename))
                embed=discord.Embed(title="Server Status", color=0x00ffff)
                embed.set_author(name=statuscode)
                embed.add_field(name="Identifier", value=id, inline=True)
                embed.add_field(name="Status", value=server_status.capitalize(), inline=True)
                embed.add_field(name="", value="yellowcircle", inline=True) # Emoji line
                embed.add_field(name="Memory Usage", value=str(memory) + ' GB', inline=False)
                embed.add_field(name="CPU Usage", value=str(cpu_usage) + '%', inline=True)
                embed.add_field(name="IP:PORT", value=allocation + ':' + str(port), inline=True)
                embed.set_footer(text=str(ctx.author) + f" ⚫ response time: " + str(time))
                await ctx.send(embed=embed)
                # ADD REACTIONS TO START STOP AND RESTART








def setup(bot:commands.Bot):
    bot.add_cog(Panel(bot))

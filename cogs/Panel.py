import asyncio, disnake
import requests, os
from dotenv import load_dotenv
load_dotenv('config.env')
from disnake.ext import commands

PTERO_API_KEY = os.getenv('PTERODACTYL_API_KEY')
ptero_url = os.getenv('pterodactylURL')
url = f'{ptero_url}/api/client'


class Panel(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.slash_command(name = "servers", description="Lists all available servers")
    async def servers(self, ctx):
        await ctx.send('Requesting data...')

        headers = {
            "Authorization": f"Bearer {PTERO_API_KEY}",
            "Accept": "application/json"
        }

        data = requests.get(url, headers=headers, timeout=10)
        server_names = []
        server_identifiers = []
        time = round(data.elapsed.microseconds / 1000)


        for server in data.json()['data']:

            server_names.append(server['attributes'] ['name'])

        for server in data.json()['data']:

            server_identifiers.append(server['attributes'] ['identifier'])

        embed=disnake.Embed(title="Available Servers", color=0x1835e7)
        embed.add_field(name="Name", value='\n'.join(server_names), inline=True)
        embed.add_field(name="Identifier", value='\n'.join(server_identifiers), inline=True)
        embed.set_footer(text=f'{str(ctx.author)} ⚫ response time: {str(time)}ms')
        await ctx.edit_original_response(content=None, embed=embed)
        server_names.clear()
        server_identifiers.clear()

    @commands.slash_command(name = "status", description="Status for server ID (Used with /servers)")
    async def status(self, ctx, identifier:str):
        await ctx.send("Querying node...")
        #Query for resources API (status, uptime, memory usage, etc)
        url = f'{url}/servers/{identifier}/resources'
        headers = {
            "Authorization": f"Bearer {PTERO_API_KEY}",
            "Accept": "application/json"
        }

        dataresources = requests.get(url, headers=headers, timeout=10)
        server_status = dataresources.json()['attributes']['current_state']
        memory_unmathed = dataresources.json()['attributes']['resources']['memory_bytes']

        cpu_raw = dataresources.json()['attributes']['resources']['cpu_absolute']
        cpu_usage = round(cpu_raw, 2)
        memory = round(memory_unmathed / 1000000000, 2)

        await ctx.edit_original_response(content="Querying panel...")

        #Query for name, allocation, port
        url_name = f'{url}/servers/{identifier}'
        dataname = requests.get(url_name, headers=headers, timeout=10)
        name = dataname.json()['attributes']['name']

        for server in dataname.json()['attributes']['relationships']['allocations']['data']:
            allocation = server['attributes']['ip_alias']

        for server in dataname.json()['attributes']['relationships']['allocations']['data']:
            port = server['attributes']['port']


        statusresource = dataresources.status_code
        statusname = dataname.status_code
        statuscode = f'resource: {str(statusresource)} name: {str(statusname)}'
        timeresource = round(dataresources.elapsed.microseconds / 1000)
        timename = round(dataname.elapsed.microseconds / 1000)
        time = timeresource + timename / 2


        if server_status == "running":
            embed=disnake.Embed(title="Server Status", color=0x22dbdd)
            embed.add_field(name="Name", value=name, inline=True)
            embed.add_field(name="Status", value=f"{server_status.capitalize()}    🟢", inline=False)
            embed.add_field(name="Memory Usage", value=f'{str(memory)} GB', inline=False)
            embed.add_field(name="CPU Usage", value=f'{str(cpu_usage)}%', inline=False)
            embed.add_field(name="IP:PORT", value=f'{allocation}:{str(port)}', inline=False)
            embed.set_footer(text=f"{str(ctx.author)} ⚫ response time: {str(time)}")
            message = await ctx.edit_original_response(content=None, embed=embed)
            # ADD REACTIONS TO START STOP AND RESTART

            list_of_emojis = ['🔴','🟡']

            for emoji in list_of_emojis:
                await message.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in list_of_emojis

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
                print(reaction)
            except asyncio.TimeoutError:
                print('timed out')
                return await message.add_reaction('⌛️')


            if str(reaction.emoji) == "🟡":
                print('yellow')
                message = await ctx.followup.send('Sending restart request...')
                url = f'{url}/servers/{identifier}/power'
                headers = {
                    "Authorization": f"Bearer {PTERO_API_KEY}",
                    "Accept": "application/json"
                }
                payload = {'signal': 'restart'}
                response = requests.post(url, headers=headers, data=payload, timeout=10)
                if response.status_code == 204:
                    await message.edit('Request approved')
                else:
                    await message.edit(content=f'{response.status_code} - Request rejected: {response}')
                return

            if str(reaction.emoji) == "🔴":
                print('red')
                message = await ctx.followup.send('Sending stop request...')
                url = f'{url}/servers/{identifier}/power'
                headers = {
                    "Authorization": f"Bearer {PTERO_API_KEY}",
                    "Accept": "application/json"
                }
                payload = {'signal': 'stop'}
                response = requests.post(url, headers=headers, data=payload, timeout=10)
                if response.status_code == 204:
                    await message.edit('Request approved')
                else:
                    await message.edit(content=f'{response.status_code} - Request rejected: {response}')
                return

            else:
                print('something shitty happened')
                await ctx.send('if you can read this, something fucked up somewhere and i have no idea why (try running the command again)')





        elif server_status == "offline":
            embed=disnake.Embed(title="Server Status", color=0xdd2422)
            embed.add_field(name="Name", value=name, inline=True)
            embed.add_field(name="Status", value=f'{server_status.capitalize()}    🔴', inline=True)
            embed.set_footer(text=f'{str(ctx.author)} ⚫ response time: {str(time)}')
            message = await ctx.followup.send(content=None, embed=embed)
            # ADD REACTIONS TO START STOP AND RESTART

            list_of_emojis = ['🟢']

            for emoji in list_of_emojis:
                await message.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in list_of_emojis

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
                print(reaction)
            except asyncio.TimeoutError:
                print('timed out')
                return await message.add_reaction('⌛️')

            if str(reaction.emoji) == "🟢":
                message = await ctx.followup.send('Sending start request...')
                url = f'{url}/servers/{identifier}/power'
                headers = {
                    "Authorization": f"Bearer {PTERO_API_KEY}",
                    "Accept": "application/json"
                }
                payload = {'signal': 'start'}
                response = requests.post(url, headers=headers, data=payload, timeout=10)
                if response.status_code == 204:
                    await message.edit('Request approved')
                else:
                    await message.edit(content=f'{response.status_code} - Request rejected: {response}')
                return

            else:
                print('something shitty happened')
                await ctx.send('if you can read this, something fucked up somewhere and i have no idea why (try running the command again)')



        elif server_status == "starting":
            embed=disnake.Embed(title="Server Status", color=0xe7ca18)
            embed.add_field(name="Name", value=name, inline=True)
            embed.add_field(name="Status", value=f'{server_status.capitalize()}    🟡', inline=True)
            embed.add_field(name="Memory Usage", value=str(memory) + ' GB', inline=False)
            embed.add_field(name="CPU Usage", value=str(cpu_usage) + '%', inline=True)
            embed.add_field(name="IP:PORT", value=allocation + ':' + str(port), inline=True)
            embed.set_footer(text=f'{str(ctx.author)} ⚫ response time: {str(time)}ms')
            message = await ctx.followup.send(content=None, embed=embed)
            # ADD REACTIONS TO START STOP AND RESTART

            list_of_emojis = ['🔴','🟡']

            for emoji in list_of_emojis:
                await message.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in list_of_emojis

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
                print(reaction)
            except asyncio.TimeoutError:
                print('timed out')
                return message.add_reaction('⌛️')


            if str(reaction.emoji) == "🟡":
                print('yellow')
                message = await ctx.followup.send('Sending restart request...')
                url = f'{url}/servers/{identifier}/power'
                headers = {
                    "Authorization": f"Bearer {PTERO_API_KEY}",
                    "Accept": "application/json"
                }
                payload = {'signal': 'restart'}
                response = requests.post(url, headers=headers, data=payload, timeout=10)
                if response.status_code == 204:
                    await message.edit(content='Request approved')
                else:
                    await message.edit(content=f'{response.status_code} - Request rejected: {response}')
                return

            if str(reaction.emoji) == "🔴":
                print('red')
                message = await ctx.followup.send('Sending stop request...')
                url = f'{url}/servers/{identifier}/power'
                headers = {
                    "Authorization": f"Bearer {PTERO_API_KEY}",
                    "Accept": "application/json"
                }
                payload = {'signal': 'stop'}
                response = requests.post(url, headers=headers, data=payload, timeout=10)
                if response.status_code == 204:
                    await message.edit(content='Request approved')
                else:
                    await message.edit(content=f'{response.status_code} - Request rejected: {response}')
                return

            else:
                print('something shitty happened')
                await ctx.send('if you can read this, something fucked up somewhere and i have no idea why (try running the command again)')

        else:
            await ctx.send('HTTPS Status Code: ' + statuscode)
            await ctx.send('Response time for resource request:' + str(timeresource))
            await ctx.send('Response time for name request:' + str(timename))


def setup(bot:commands.Bot):
    bot.add_cog(Panel(bot))
import asyncio
from cgi import test
import disnake
import requests, os
from dotenv import load_dotenv
load_dotenv('config.env')
from disnake.ext import commands

API_KEY = os.getenv('API_KEY')
PanelDomain = os.getenv('PanelDomain')


class Panel(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} Panel has loaded mr furry')

    @commands.command(name = "servers")
    async def servers(self, ctx, number):

        url = f'https://{PanelDomain}/api/client'
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Accept": "application/json"
        }
        data = requests.get(url, headers=headers)
        server_names = []
        server_identifiers = []
        time = round(data.elapsed.microseconds / 1000)


        message = await ctx.send('Requesting data...')
   
        embed = disnake.Embed()
        embed.add_field("Numbers", "\n".join(map(str, range(1, len(server_identifiers) + 1))))
        embed.add_field("Name", "\n".join(server_names for server in server))
        embed.add_field("Identifier", "\n".join(server_identifiers for server in servers))
        ctx.send(embed)





# --------------------------------------------------------------------------------------------------------
#         url = f'https://{PanelDomain}/api/client'
#         headers = {
#             "Authorization": f"Bearer {API_KEY}",
#             "Accept": "application/json"
#         }

#         data = requests.get(url, headers=headers)
#         server_names = []
#         server_identifiers = []
#         time = round(data.elapsed.microseconds / 1000)
  

#         for server in data.json()['data']:

#             server_names.append(server['attributes'] ['name'])

#         for server in data.json()['data']:

#             server_identifiers.append(server['attributes'] ['identifier'])

#         for n,item in enumerate(server_identifiers):
#             print(f'{n}: {item}')
#             embed.add_field(name=None)

#         embed=disnake.Embed(title="Available Servers", color=0x1835e7)
#         embed.add_field(name="Name", value='\n'.join(server_names), inline=True)
#         embed.add_field(name="Identifier", value='\n'.join(server_identifiers), inline=True)
#         embed.set_footer(text=str(ctx.author) + f" ⚫ response time: " + str(time) + 'ms')
#         await message.edit(content=None, embed=embed)
#         server_names.clear()
#         server_identifiers.clear()

    @commands.command(name = "status", aliases=['restart', 'start'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def start(self, ctx, id = 'null'):
        if id == 'null':
            await ctx.send("Please provide the identifier")
        elif id == '4529cae6' and ctx.author != self.bot.owner:
            await ctx.send('lol no')
        else:
            message = await ctx.send("Querying node...")
            #Query for resources API (status, uptime, memory usage, etc)
            url = f'https://{PanelDomain}/api/client/servers/{id}/resources'
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Accept": "application/json"
            }

            dataresources = requests.get(url, headers=headers)

            server_status = dataresources.json()['attributes']['current_state']
            
            memory_unmathed = dataresources.json()['attributes']['resources']['memory_bytes']

            cpu_raw = dataresources.json()['attributes']['resources']['cpu_absolute']

            cpu_usage = round(cpu_raw, 2)


            memory = round(memory_unmathed / 1000000000, 2)

            await message.edit(content="Querying panel...")

            #Query for name, allocation, port
            url_name = f'https://{PanelDomain}/api/client/servers/{id}'

            dataname = requests.get(url_name, headers=headers)

            name = dataname.json()['attributes']['name']

            for server in dataname.json()['attributes']['relationships']['allocations']['data']:

                allocation = server['attributes']['ip_alias']

            for server in dataname.json()['attributes']['relationships']['allocations']['data']:

                port = server['attributes']['port']


            statusresource = dataresources.status_code
            statusname = dataname.status_code
            statuscode = "resource: " + str(statusresource) + " name: " + str(statusname)
            timeresource = round(dataresources.elapsed.microseconds / 1000)
            timename = round(dataname.elapsed.microseconds / 1000)
            time = timeresource + timename / 2



            if server_status == "running":
                embed=disnake.Embed(title="Server Status", color=0x22dbdd)
                embed.add_field(name="Name", value=name, inline=True)
                embed.add_field(name="Status", value=server_status.capitalize(), inline=True)
                embed.add_field(name="Icon", value="🟢", inline=True) # Emoji line
                embed.add_field(name="Memory Usage", value=str(memory) + ' GB', inline=False)
                embed.add_field(name="CPU Usage", value=str(cpu_usage) + '%', inline=True)
                embed.add_field(name="IP:PORT", value=allocation + ':' + str(port), inline=True)
                embed.set_footer(text=str(ctx.author) + f" ⚫ response time: " + str(time))
                await message.edit(content=None, embed=embed)
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
                    for emoji in list_of_emojis:
                        await message.remove_reaction(emoji)

                # if str(reaction.emoji) == "🟢":
                #     print('green')
                #     await ctx.send('Sending start request...')
                #     url = f'https://{PanelDomain}/api/client/servers/{id}/power'
                #     headers = {
                #         "Authorization": f"Bearer {API_KEY}",
                #         "Accept": "application/json"
                #     }
                #     payload = {'signal': 'start'}
                #     response = requests.post(url, headers=headers, data=payload)
                #     if response.status_code == 204:
                #         await ctx.send('Request approved')
                #     else:
                #         await ctx.send('Something unexpected happened: ' + response)
                #     return

                if str(reaction.emoji) == "🟡":
                    print('yellow')
                    await ctx.send('Sending restart request...')
                    url = f'https://{PanelDomain}/api/client/servers/{id}/power'
                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Accept": "application/json"
                    }
                    payload = {'signal': 'restart'}
                    response = requests.post(url, headers=headers, data=payload)
                    if response.status_code == 204:
                        await ctx.send('Request approved')
                    else:
                        await ctx.send('Something unexpected happened: ' + response)
                    return

                if str(reaction.emoji) == "🔴":
                    print('red')
                    await ctx.send('Sending stop request...')
                    url = f'https://{PanelDomain}/api/client/servers/{id}/power'
                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Accept": "application/json"
                    }
                    payload = {'signal': 'stop'}
                    response = requests.post(url, headers=headers, data=payload)
                    if response.status_code == 204:
                        await ctx.send('Request approved')
                    else:
                        await ctx.send('Something unexpected happened: ' + response)
                    return

                else:
                    print('something shitty happened')
                    await ctx.send('if you can read this, something fucked up somewhere and i have no idea why')





            elif server_status == "offline":
                embed=disnake.Embed(title="Server Status", color=0xdd2422)
                embed.add_field(name="Name", value=name, inline=True)
                embed.add_field(name="Status", value=server_status.capitalize(), inline=True)
                embed.add_field(name="Icon", value="🔴", inline=True) # Emoji line
                embed.set_footer(text=str(ctx.author) + f" ⚫ response time: " + str(time))
                await message.edit(content=None, embed=embed)
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
                    for emoji in list_of_emojis:
                        await message.remove_reaction(emoji)

                if str(reaction.emoji) == "🟢":
                    print('green')
                    await ctx.send('Sending start request...')
                    url = f'https://{PanelDomain}/api/client/servers/{id}/power'
                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Accept": "application/json"
                    }
                    payload = {'signal': 'start'}
                    response = requests.post(url, headers=headers, data=payload)
                    if response.status_code == 204:
                        await ctx.send('Request approved')
                    else:
                        await ctx.send('Something unexpected happened: ' + response)
                    return

                # if str(reaction.emoji) == "🟡":
                #     print('yellow')
                #     await ctx.send('Sending restart request...')
                #     url = f'https://{PanelDomain}/api/client/servers/{id}/power'
                #     headers = {
                #         "Authorization": f"Bearer {API_KEY}",
                #         "Accept": "application/json"
                #     }
                #     payload = {'signal': 'restart'}
                #     response = requests.post(url, headers=headers, data=payload)
                #     if response.status_code == 204:
                #         await ctx.send('Request approved')
                #     else:
                #         await ctx.send('Something unexpected happened: ' + response)
                #     return

                # if str(reaction.emoji) == "🔴":
                #     print('red')
                #     await ctx.send('Sending stop request...')
                #     url = f'https://{PanelDomain}/api/client/servers/{id}/power'
                #     headers = {
                #         "Authorization": f"Bearer {API_KEY}",
                #         "Accept": "application/json"
                #     }
                #     payload = {'signal': 'stop'}
                #     response = requests.post(url, headers=headers, data=payload)
                #     if response.status_code == 204:
                #         await ctx.send('Request approved')
                #     else:
                #         await ctx.send('Something unexpected happened: ' + response)
                #     return

                else:
                    print('something shitty happened')
                    await ctx.send('if you can read this, something fucked up somewhere and i have no idea why')



            elif server_status == "starting":
                await ctx.send('starting')
                embed=disnake.Embed(title="Server Status", color=0xe7ca18)
                embed.add_field(name="Name", value=name, inline=True)
                embed.add_field(name="Status", value=server_status.capitalize(), inline=True)
                embed.add_field(name="Icon", value="🟡", inline=True) # Emoji line
                embed.add_field(name="Memory Usage", value=str(memory) + ' GB', inline=False)
                embed.add_field(name="CPU Usage", value=str(cpu_usage) + '%', inline=True)
                embed.add_field(name="IP:PORT", value=allocation + ':' + str(port), inline=True)
                embed.set_footer(text=str(ctx.author) + f" ⚫ response time: " + str(time))
                await message.edit(content=None, embed=embed)
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
                    for emoji in list_of_emojis:
                        await message.remove_reaction(emoji)

                # if str(reaction.emoji) == "🟢":
                #     print('green')
                #     await ctx.send('Sending start request...')
                #     url = f'https://{PanelDomain}/api/client/servers/{id}/power'
                #     headers = {
                #         "Authorization": f"Bearer {API_KEY}",
                #         "Accept": "application/json"
                #     }
                #     payload = {'signal': 'start'}
                #     response = requests.post(url, headers=headers, data=payload)
                #     if response.status_code == 204:
                #         await ctx.send('Request approved')
                #     else:
                #         await ctx.send('Something unexpected happened: ' + response)
                #     return

                if str(reaction.emoji) == "🟡":
                    print('yellow')
                    message = await ctx.send('Sending restart request...')
                    url = f'https://{PanelDomain}/api/client/servers/{id}/power'
                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Accept": "application/json"
                    }
                    payload = {'signal': 'restart'}
                    response = requests.post(url, headers=headers, data=payload)
                    if response.status_code == 204:
                        await message.edit(content='Request approved')
                    else:
                        await message.edit(content=response.status_code + ' - Something unexpected happened: ' + response)
                    return

                if str(reaction.emoji) == "🔴":
                    print('red')
                    message = await ctx.send('Sending stop request...')
                    url = f'https://{PanelDomain}/api/client/servers/{id}/power'
                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Accept": "application/json"
                    }
                    payload = {'signal': 'stop'}
                    response = requests.post(url, headers=headers, data=payload)
                    if response.status_code == 204:
                        await message.edit(content='Request approved')
                    else:
                        await message.edit(content=response.status_code + ' - Something unexpected happened: ' + response)
                    return

                else:
                    print('something shitty happened')
                    await ctx.send('if you can read this, something fucked up somewhere and i have no idea why')



            else:
                await ctx.send('HTTPS Status Code: ' + statuscode)
                await ctx.send('Response time for resource request:' + str(timeresource))
                await ctx.send('Response time for name request:' + str(timename))
                embed=disnake.Embed(title="Response from the API", color=0xaa33cc)
                embed.set_author(name=statuscode)
                embed.add_field(name="Name", value=name, inline=True)
                embed.add_field(name="Status", value=server_status.capitalize(), inline=True)
                embed.add_field(name="Icon", value="🟡", inline=True) # Emoji line
                embed.add_field(name="Memory Usage", value=str(memory) + ' GB', inline=False)
                embed.add_field(name="CPU Usage", value=str(cpu_usage) + '%', inline=True)
                embed.add_field(name="IP:PORT", value=allocation + ':' + str(port), inline=True)
                embed.set_footer(text=str(ctx.author) + f" ⚫ response time: " + str(time))
                await ctx.send(embed=embed)
                await ctx.send('Something unexpected happened, pls ping Happyllama25#0001 about this')


def setup(bot:commands.Bot):
    bot.add_cog(Panel(bot))
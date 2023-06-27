import disnake
import time
import socket
import requests
from disnake.ext import commands


class Titanfall(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="titanfall", description="List of active Northstar servers")
    async def command_name(self, ctx):
        await ctx.response.defer()

        try:
            url = "https://northstar.tf/client/servers"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as error:
            await ctx.send(f"An error occurred while fetching server data: {str(error)}")
            return
        except ValueError as error:
            await ctx.send(f"An error occurred while processing server data: {str(error)}")
            return

        servers = data
        server_count = len(data)

        priority_server = None
        priority_index = None
        for index, server in enumerate(servers):
            if "happyllama25" in server["name"].lower():
                priority_server += server
                priority_index = index

        message = f"```diff\n+ {server_count} servers were found - displaying first 5 results\n\n"

        if priority_server:
            servers.pop(priority_index)
            servers.insert(0, priority_server)
        else:
            message += "- Happyllama25 servers not found\n\n"

        # Sort the servers by player count in descending order
        servers.sort(key=lambda server: server["playerCount"], reverse=True)
        total_players = 0

        for server in servers[:5]:
            message += f"{server['name']}\n"
            if server['playerCount'] == server['maxPlayers']:
                message += f"- {server['playerCount']} / {server['maxPlayers']} players connected\n"
            else:
                message += f"+ {server['playerCount']} / {server['maxPlayers']} players connected\n"
            message += f"+ Playing {server['playlist']} on {server['map']}\n\n"
            if server['hasPassword']:
                message += "- Password protected\n"
            total_players += server['playerCount']
        for server in servers:
            total_players += server['playerCount']

        message += f"\n+Global total Players: {total_players}"

        await ctx.edit_original_response(f"{message}```")




def setup(bot):
    bot.add_cog(Titanfall(bot))

import disnake
import time
import socket
import requests
from disnake.ext import commands


class Titanfall(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="titanfall", description="List of active Northstar servers")
    async def titanfall(self, ctx):
        await ctx.response.defer()
        servers = []

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


        priority_server = []
        for server in servers:
            if "happyllama25" in server["name"].lower():
                priority_server.append(server)

        message = f"```diff\n+ {server_count} servers were found - displaying first 5 results\n\n"

        if priority_server:
            for ps in priority_server:
                servers.remove(ps)
            servers = priority_server + servers # Add priority servers to the start of the servers list
        else:
            message += "- Happyllama25 servers not found\n\n"

        # If you want to move all priority servers to the front:
        for server in reversed(priority_server):
            servers.remove(server)
            servers.insert(0, server)
        total_players = 0

        for server in servers[:5]:
            if not isinstance(server, dict):
                print("Unexpected server format:", server)
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

# CatBot

## Description
CatBot is a Discord bot written in Python, using the Disnake library. It was initially created to allow friends to start and join a Minecraft Server without manual interaction. It has since evolved to include a variety of features, including interacting with the Pterodactyl Panel API to start and stop servers/programs remotely.

## Features
- Interaction with Pterodactyl Panel API
- Video downloading with yt-dlp
- Titanfall 2 Northstar server lookup and stats
- OpenAI GPT-3.5 interaction
- Admin commands
- Misc commands (QR Code generation, cat facts and pics, etc.)

## Installation
1. Clone this repository.
2. Install the required Python packages using pip: `pip install -r requirements.txt`
3. Place relevant API keys in `.env` file

## Usage
All commands are Discord slash commands

## Contributing
Just make a pull request or an issue if you have a comment to make or a feature to add/request.

# Old README
This is my first coding project I wrote, it was created so that my friends and others could start and join a Minecraft Server that I had on my PC without me needing to manually start it for them every time.

My goal was to ultimately get more people into joining the server and interacting with each other and to also cut out the need to manually start servers from the host machine.

I started writing it in Python 3.9 and discord.py 1.7.3 but then migrated to Disnake 2.4.0

I then further developed this project to perform an API request to a [Pterodactyl Panel](https://pterodactyl.io/) to start and stop servers/programs remotely through Discord.


and now i just mess about with it when i have the time

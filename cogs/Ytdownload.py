import disnake
from disnake.ext import commands
import yt_dlp
import os
import time
import asyncio

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

class Ytdownload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_update = 0  # Add a variable to track the time of the last update

    @commands.slash_command(name="download", description="Download a YouTube video")
    async def download(self, ctx, url: str):
        self.ctx = ctx  # Store the ctx object as an instance variable
        ydl_opts = {
            'format': 'best',
            'logger': MyLogger(),
            'progress_hooks': [self.my_hook],
            'outtmpl': 'downloaded_video.%(ext)s'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            await ctx.send(f"Downloading {video_title}...")
            ydl.download([url])
            video_file = 'downloaded_video.mp4'
            if os.path.getsize(video_file) > 25 * 1024 * 1024:  # Convert 25MB to bytes
                await ctx.edit_original_response(content=f"The video '{video_title}' is too large to send through Discord.")
            else:
                await ctx.edit_original_response(content=f"Downloaded {video_title}!")
                with open(video_file, 'rb') as fp:
                    await ctx.send(file=disnake.File(fp, 'new_video.mp4'))

    def my_hook(self, status):
        if status.get('status') == 'downloading':
            loop = asyncio.get_event_loop()
            loop.create_task(self.update_message(status['filename'], status['_percent_str'], status['_eta_str']))

    async def update_message(self, filename, percent, eta):
        now = time.time()
        if now - self.last_update < 5 or percent != 100.0:  # If less than 5 seconds have passed since the last update...
            return  # ...don't send an update.
        self.last_update = now  # Update the time of the last update.
        await self.ctx.edit_original_response(content=f"Downloading {filename}\nProgress: {percent}\nETA: {eta}")


def setup(bot):
    bot.add_cog(Ytdownload(bot))

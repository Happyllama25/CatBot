import disnake
import re
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

    @commands.slash_command(name='search', description='Search for a YouTube video')
    async def search(self, ctx, *, query: str):
        await ctx.response.defer()
        await ctx.edit_original_response(content=f"congrats, you found a command i have not finished yet, you get a cookie :cookie: tell happyllama25 to get his ass out of bed and finish this command")

    @commands.slash_command(name="download", description="Download a YouTube video")
    async def download(self, ctx, url: str):
        await ctx.response.defer()
        self.ctx = ctx  # Store the ctx object as an instance variable

        # def less_than_a_minute(info, *, incomplete):
        #     """Download only videos longer than a minute (or with unknown duration)"""
        #     duration = info.get('duration')
        #     if duration and duration > 60:
        #         return 'The video is too long'

        ydl_opts = {
            'format': 'best[ext=mp4]',
            'logger': MyLogger(),
            'progress_hooks': [self.my_hook],
            'outtmpl': 'downloaded_video.%(ext)s'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            safe_title = re.sub(r'\W+', '_', video_title, flags=re.UNICODE)
            video_file = f'{safe_title[:24]}.mp4'
            os.rename('downloaded_video.mp4', video_file)

            await ctx.edit_original_response(f"Downloading {video_title}...")
            ydl.download([url])
            if os.path.getsize(video_file) > 25 * 1024 * 1024:  # Convert 25MB to bytes
                await ctx.edit_original_response(content=f"The video '{video_title}' is too large to send through Discord. :( LEGALIZE NUCLEAR BOMBS >:)")
                os.remove(video_file)
            else:
                await ctx.edit_original_response(content=f"Downloaded {video_title}! Uploading...")
                with open(video_file, 'rb') as fp:
                    await ctx.send(file=disnake.File(fp, 'new_video.mp4'))
                os.remove(video_file)

    async def my_hook(self, status):
        if status.get('status') == 'downloading':
            loop = asyncio.get_event_loop()
            # Create a new task for update_message and run it immediately
            loop.run_until_complete(self.update_message(status['filename'], status['_percent_str'], status['_eta_str']))

    async def update_message(self, filename, percent, eta):
        now = time.time()
        if now - self.last_update < 1 or percent == 100.0:  # If less than 5 seconds have passed since the last update...
            return  # ...don't send an update.
        self.last_update = now  # Update the time of the last update.
        await self.ctx.edit_original_response(content=f"Downloading {filename}\nProgress: {percent}\nETA: {eta}")


def setup(bot):
    bot.add_cog(Ytdownload(bot))

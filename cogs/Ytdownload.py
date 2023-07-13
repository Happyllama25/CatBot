import disnake
import re
from disnake.ext import commands
import yt_dlp
import os
import time
import asyncio
import concurrent.futures

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
        self.progress = None
        self.download_in_progress = False
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    @commands.slash_command(name='search', description='Search for a YouTube video')
    async def search(self, ctx, *, query: str):
        await ctx.response.defer()
        await ctx.edit_original_response(content=f"congrats, you found a command i have not finished yet, you get a cookie :cookie: tell happyllama25 to get his ass out of bed and finish this command")

    @commands.slash_command(name="download", description="Download a YouTube video")
    async def download(self, ctx, url: str):
        if self.download_in_progress == True:
            await ctx.send("A download is already in progress. Please wait for it to finish before starting a new download.")
            return

        await ctx.response.defer()

        self.download_in_progress = True
        # Start the send_progress_updates coroutine
        update_task = asyncio.create_task(self.send_progress_updates())

        ydl_opts = {
            'format': 'best[ext=mp4]',
            'logger': MyLogger(),
            'progress_hooks': [lambda status: self.report_progress(ctx, status)],
            'outtmpl': 'downloaded_video.%(ext)s'
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_title = info_dict.get('title', None)
                safe_title = re.sub(r'\W+', '_', video_title, flags=re.UNICODE)
                video_file = f'{safe_title[:24]}.mp4'
                self.filename = video_file

                self.message = await ctx.edit_original_response(f"Downloading **{video_title}**")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(self.executor, lambda: ydl.download([url]))
                os.rename('downloaded_video.mp4', video_file)
                if os.path.getsize(video_file) > 25 * 1024 * 1024:  # Convert 25MB to bytes
                    await ctx.edit_original_response(content=f"The video '{video_title}' is too big for discord to handle :( discord is a big meanie\nLEGALIZE NUCLEAR BOMBS >:)")
                    os.remove(video_file)
                else:
                    await ctx.edit_original_response(content=f"Downloaded **{video_title}**! Uploading...")
                    with open(video_file, 'rb') as fp:
                        await ctx.send(file=disnake.File(fp, f'{video_file}'))
                    os.remove(video_file)
        except yt_dlp.utils.DownloadError as e:
            await ctx.edit_original_response(content=f"error occur :(\n{e}")

        update_task.cancel()
        self.download_in_progress = False

    def report_progress(self, ctx, status):
        print("report_progress")
        if status.get('status') == 'downloading':
            print("setting message variables")
            filename = self.filename
            percent = status['_percent_str']
            eta = status['_eta_str']
            self.progress = f"Downloading `{filename}`\nProgress: {percent}\nETA: {eta}"

    async def send_progress_updates(self):
        print("send_progress_updates")
        last_update = time.time()
        while self.download_in_progress:
            print("while loop")
            print("download_in_progress:", self.download_in_progress)
            if time.time() - last_update >= 1:
                print("update message")
                await self.message.edit(content=self.progress)  # Edit the message directly
                last_update = time.time()
            await asyncio.sleep(1)
            print("end of iteration")
        print("loop finished")


def setup(bot):
    bot.add_cog(Ytdownload(bot))
import disnake
import re
from disnake.ext import commands
import yt_dlp
import os
import time
import asyncio
import subprocess
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
        self.progress = ". . . - - - . . ."
        self.download_in_progress = False
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    @commands.slash_command(name='search', description='Search for a YouTube video')
    async def search(self, ctx, *, query: str):
        await ctx.response.defer()
        await ctx.edit_original_response(content=f"congrats, you found a command i have not finished yet, you get a cookie :cookie: tell happyllama25 to get his ass out of bed and finish this command")

    @commands.slash_command(name="download", description="Download a YouTube video")
    async def download(self, ctx, url: str, options: str = commands.Param(default="Video+Audio", choices=["Video+Audio","Video","Audio"], description="What format to download the video in"), webm: bool = commands.Param(description="Whether to download in .webm (Might be a smaller file if too big normally)", default=False)):
        if self.download_in_progress == True:
            await ctx.send("A download is already in progress. Please wait for it to finish before starting a new download.")
            return

        if webm == False:
            if options == "Video+Audio":
                config = 'bestvideo.2+bestaudio[ext=mp4]/best[ext=mp4]'
            elif options == "Video":
                config = 'worstvideo.2[ext=mp4]'
            elif options == "Audio":
                config = 'bestaudio[ext=m4a]'
        else:
            if options == "Video+Audio":
                config = 'bestvideo+bestaudio[ext=webm]/best[ext=webm]'
            elif options == "Video":
                config = 'bestvideo[ext=webm]'
            elif options == "Audio":
                config = 'bestaudio[ext=m4a]'


        ydl_opts = {
            'format': f'{config}',
            'logger': MyLogger(),
            'progress_hooks': [lambda status: self.report_progress(ctx, status)],
            'outtmpl': 'downloaded_video.%(ext)s'
        }


        await ctx.response.defer()

        self.download_in_progress = True
        # Start the send_progress_updates coroutine
        update_task = asyncio.create_task(self.send_progress_updates())

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_title = info_dict.get('title', None)
                safe_title = re.sub(r'\W+', '_', video_title, flags=re.UNICODE)

                if webm:
                    ext = "webm"
                elif options == "Audio":
                    ext = "m4a"
                else:
                    ext = "mp4"



                video_file = f'{safe_title[:32]}.{ext}'
                self.filename = video_file #this is used in the update progress thingy

                self.message = await ctx.edit_original_response(f"Downloading **{video_title}**")

                loop = asyncio.get_event_loop()
                await loop.run_in_executor(self.executor, lambda: ydl.download([url]))

                self.download_in_progress = False
                # Check the codec of the video
                command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', f'downloaded_video.{ext}']
                codec = subprocess.check_output(command).decode('utf-8').strip()

                if codec == 'hevc':  # 'hevc' stands for H.265
                    # Convert to H.264 using FFmpeg
                    await ctx.edit_original_response(content=f"Video is H.265, Converting to H.264 for compatibility...")

                    output_file = f"converted_downloaded_video.{ext}"
                    command = ['ffmpeg', '-i', f"downloaded_video.{ext}", '-c:v', 'libx264', '-c:a', 'copy', output_file]
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

                    # Parse ffmpeg output for progress and update message
                    last_update = time.time() + 1  # This ensures the first line is parsed
                    for line in process.stdout:
                        if "frame=" in line and time.time() - last_update > 1:  # This checks for lines that show progress and ensures at least 1 second between updates
                            await ctx.edit_original_response(content=f"Converting: {line.strip()}")
                            last_update = time.time()

                    # there gonnabe a downloaded_video.mp4 AND a converted_downloaded_video.mp4
                    os.remove(f'downloaded_video.{ext}')
                    os.rename(output_file, video_file)

                else:
                    os.rename(f'downloaded_video.{ext}', video_file)
                    self.download_in_progress = False
                size = os.path.getsize(video_file)
                if size > 25 * 1024 * 1024:
                    await ctx.edit_original_response(content=f"The video '{video_title}' is too big for discord to handle ({size / 1024 / 1024:.2f}MB > 25MB) :( discord is a big meanie\nLEGALIZE NUCLEAR BOMBS >:)")
                    os.remove(video_file)
                else:
                    await ctx.edit_original_response(content=f"Downloaded **{video_title}**! Uploading {size / 1024 / 1024:.2f}MB...")
                    with open(video_file, 'rb') as fp:
                        await ctx.send(file=disnake.File(fp, f'{video_file}'))
                    os.remove(video_file)
        except yt_dlp.utils.DownloadError as e:
            await ctx.edit_original_response(content=f"error occur :(\n```ansi\n{e}\n```")
            self.download_in_progress = False
        except Exception as e:
            await ctx.edit_original_response(content=f"worser error occur :(\n```ansi\n{e}\n```")
            self.download_in_progress = False

        update_task.cancel()
        print("cancelled update loop and set var to false")

    def report_progress(self, ctx, status):
        if status.get('status') == 'downloading':
            filename = self.filename
            percent = status['_percent_str']
            eta = status['_eta_str']
            self.progress = f"Downloading `{filename}`\nProgress: {percent}\nETA: {eta}"

    async def send_progress_updates(self):
        last_update = time.time() + 1
        while self.download_in_progress:
            if time.time() - last_update >= 1:
                await self.message.edit(content=self.progress)  # Edit the message directly
                last_update = time.time()
            else:
                await asyncio.sleep(1)
        print("loop finished")


def setup(bot):
    bot.add_cog(Ytdownload(bot))
import disnake
from disnake.ext import commands
import yt_dlp
import os
import logging
import re
import asyncio
import time
import subprocess
from pathlib import Path


RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
RESET = "\033[0m"

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
        self.download_in_progress = False
        self.last_update = 0
        self.lock = asyncio.Lock()

    @commands.slash_command(name="download", description="Download a YouTube video")
    async def download(self, ctx, url: str = commands.Param(name='url', description="The URL to the video (Also works with tiktok and some* other video hosts)"), quality: str = commands.Param(default="best", choices={"Best Audio+Video": "best", "Best Audio": "bestaudio", "Best Video": "bestvideo", "Worst Audio+Video": "worst", "Worst Audio": "worstaudio", "Worst Video": "worstvideo"}, name="quality", description="Defaults to Best Audio + Video")):
        if self.download_in_progress:
            await ctx.send(content="A download is already in progress. Please wait for it to finish.")
            return

        await ctx.response.defer()
        self.download_in_progress = True

        try:
            video_file, video_title = await self.download_video(ctx, url, quality)
            print("Looking for video file:", video_file)
            if not os.path.exists(video_file):
                raise FileNotFoundError("Downloaded video file not found on disk.")

            await self.send_video(ctx, video_file, video_title)
        except Exception as e:
            await ctx.send(content=f"An error occurred: {e}")
        finally:
            self.download_in_progress = False
            if os.path.exists(video_file):
                os.remove(video_file)


    async def download_video(self, ctx, url, quality):
        ydl_opts = {
            'logger': MyLogger(),
            'progress_hooks': [lambda status: self.bot.loop.create_task(self.ytdl_progress_hook(ctx, status))],
            'outtmpl': './output/downloaded_file.%(ext)s',
            'format': quality
        }

        if "audio" in quality:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        else:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = await asyncio.to_thread(ydl.extract_info, url, download=True)
            base_path = './output/downloaded_file'
            video_title = info_dict.get('title')


            for ext in ['mp4', 'mp3']:
                potential_path = f'{base_path}.{ext}'
                if os.path.exists(potential_path):
                    return potential_path, video_title

            original_path = ydl.prepare_filename(info_dict)
            return original_path, video_title


    async def ytdl_progress_hook(self, ctx, status):
        async with self.lock:
            current_time = time.time()
            if status.get('status') == 'downloading' and current_time - self.last_update > 1:
                filename = os.path.basename(status['filename'])
                percent = status.get('_percent_str', 'N/A')
                eta = status.get('_eta_str', 'N/A')
                progress = f"\u001b[1;37mDownloading: \u001b[0m{filename}\n\u001b[1;37mProgress: \u001b[0m{percent}\n\u001b[1;37mETA: \u001b[0m{eta}"
                await self.update_progress_message(ctx, progress)

    async def update_progress_message(self, ctx, message):
        # Define a set of Braille characters for the animation
        animation_chars = ['⠋', '⠙', '⠸', '⠴', '⠦', '⠇']
        
        # Calculate the index for the next animation character
        animation_index = int(time.time()) % len(animation_chars)
        animation_char = animation_chars[animation_index]

        # ANSI escape code for blue text
        BLUE = "\u001b[34m"
        RESET = "\u001b[0m"

        current_time = time.time()
        if current_time - self.last_update > 1:
            # Append the animated, blue character to the message
            animated_message = f"```ansi\n{message}\n\n{BLUE}{animation_char}{RESET} (If the process is frozen, run /restart and try again)```"
            await ctx.edit_original_response(content=animated_message)
            self.last_update = current_time




    async def send_video(self, ctx, video_file, video_title):
        try:
            
            size = os.path.getsize(video_file) / 1024 / 1024  # Size in MB
            if size > 25:
                
                video_file = await self.compress_file(ctx, video_file, 24)


            size = os.path.getsize(video_file) / 1024 / 1024
            file_extension = os.path.splitext(video_file)[1]
            upload_filename = f"{video_title}{file_extension}"

            await ctx.edit_original_response(content=f"Uploading {upload_filename} ({size:.2f} MB)...")
            with open(video_file, 'rb') as fp:
                await ctx.send(file=disnake.File(fp, upload_filename))
            os.remove(video_file)
        except Exception as e:
            logging.error(f"Error in sending video: {e}")
            await ctx.edit_original_response(content=f"An error occurred while sending the video: {e}")


    async def compress_file(self, ctx, video_file, target_size_MB):
        video_file_path = Path(video_file)
        target_size_kb = target_size_MB * 1024
        duration = self.get_video_duration(video_file)
        if duration <= 0:
            return video_file

        target_bitrate = int((target_size_kb * 8) / duration) - 128

        first_pass_cmd = [
            'ffmpeg', '-y', '-i', video_file, '-c:v', 'libx264', '-preset', 'medium',
            '-b:v', str(target_bitrate) + 'k', '-progress', '-', '-pass', '1', '-an', '-f', 'mp4', '/dev/null'
        ]

        await self.run_ffmpeg(ctx, first_pass_cmd, "Analysing video (1/2)")

        output_file = str(video_file_path.stem) + "_compressed.mp4"
        second_pass_cmd = [
            'ffmpeg', '-i', str(video_file_path), '-c:v', 'libx264', '-preset', 'medium',
            '-b:v', str(target_bitrate) + 'k', '-progress', '-', '-nostats', '-pass', '2', '-c:a', 'aac', '-b:a', '128k', output_file
        ]

        await self.run_ffmpeg(ctx, second_pass_cmd, "Compressing video (2/2)")

        return Path(output_file)
    
    async def run_ffmpeg(self, ctx, cmd, pass_description):
        process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

        progress_data = {}

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            line = line.decode().strip()

            # Process each line if it contains an '=' character
            if '=' in line:
                key, value = line.split('=', 1)
                progress_data[key] = value

                frame_number = progress_data.get('frame', '...')
                fps = progress_data.get('fps', '...')
                bitrate = progress_data.get('bitrate', '...')
                time_str = progress_data.get('out_time', '...').split('.')[0]
                speed = progress_data.get('speed', '...')

                progress_description = f"\u001b[1;37m{pass_description}"
                progress_time = f"\u001b[1;37mTime: {YELLOW}{time_str}"
                progress_bitrate = f"\u001b[1;37mBitrate: {YELLOW}{bitrate}"
                progress_frame = f"\u001b[1;37mFrame: {YELLOW}{frame_number}"
                progress_fps = f"\u001b[1;37mFPS: {YELLOW}{fps}"
                progress_speed = f"\u001b[1;37mSpeed: {YELLOW}{speed}"

                message = f"{progress_description}\n\n{progress_time}\n{progress_bitrate}\n{progress_frame}\n{progress_fps}\n{progress_speed}"

                # Send the message
                await self.update_progress_message(ctx, message)

        await process.wait()


    def get_video_duration(self, video_file):
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_file],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True
            )
            return float(result.stdout.decode('utf-8').strip())
        except Exception as e:
            logging.error(f"Error getting video duration: {e}")
            return 0

    def file_exists(self, file_path):
        print("Current working directory:", os.getcwd())
        print("Checking file path:", file_path)
        return os.path.exists(file_path)
    

def setup(bot):
    bot.add_cog(Ytdownload(bot))

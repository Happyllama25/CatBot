import disnake
from disnake.ext import commands, tasks
import yt_dlp
import os
import time
import asyncio
from datetime import datetime
from flask import Flask, send_from_directory, abort, render_template, url_for
from threading import Thread

# Configuration
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
PORT = 8129  # Make sure to use the same port in the URL generation

flask_app = Flask(__name__)

@flask_app.route('/downloads/<file_ID>')
def download_file(file_ID):
    return render_template('index.html', file_ID=file_ID)

@flask_app.route('/media/<file_ID>')
def serve_file(file_ID):
    try:
        return send_from_directory(DOWNLOAD_FOLDER, file_ID, as_attachment=True)
    except FileNotFoundError:
        abort(404)

def run_flask_app():
    flask_app.run(port=PORT, use_reloader=False)

class YouTubeDownloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup.start()
        self.external_ip = "smol-ash.happyllama25.net"
        
        # Start Flask app in a separate thread
        flask_thread = Thread(target=run_flask_app)
        flask_thread.daemon = True  
        flask_thread.start()

    @commands.slash_command()
    async def download(
        self, 
        ctx, 
        url: str, 
        option: str = commands.Param(choices=["video+audio", "audio"], default="video+audio"),
        quality: str = commands.Param(choices=["highest", "regular", "lowest available"], default="regular")
    ):
        message = await ctx.send(f"Starting download...")

        start_time = time.time()
        last_update_time = 0

        # Set initial format options based on user selection
        ydl_opts = {
            'outtmpl': os.path.join(self.DOWNLOAD_FOLDER, '%(title).30s.%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
            'progress_hooks': [lambda d: self.progress_hook(d, ctx, message, start_time, last_update_time)],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [info_dict])

            best_format = None

            if quality == "lowest available":
                # Find the lowest quality format
                best_format = min(
                    (f for f in formats if f.get('ext') == 'mp4' or option == "audio"),
                    key=lambda f: f.get('filesize', float('inf')),
                    default=None
                )
            elif quality == "highest":
                # Find the highest quality format
                best_format = max(
                    (f for f in formats if f.get('ext') == 'mp4' or option == "audio"),
                    key=lambda f: f.get('filesize', float('-inf')),
                    default=None
                )
            elif quality == "regular":
                # Find the best format under 1080p or highest quality audio
                for f in formats:
                    if f.get('filesize') and f.get('ext') == 'mp4' and f['height'] <= 1080:
                        best_format = f['format_id']
                        break
                if not best_format:
                    best_format = 'bestvideo[height<=1080]+bestaudio[ext=m4a]/best[height<=1080]' if option == "video+audio" else 'bestaudio[ext=m4a]/best'

            if best_format:
                ydl_opts['format'] = best_format if isinstance(best_format, str) else best_format['format_id']
            else:
                ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio[ext=m4a]/best[height<=1080]' if option == "video+audio" else 'bestaudio[ext=m4a]/best'

            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            await self.handle_upload(ctx, file_path, info_dict)

    async def progress_hook(self, d, ctx, message, start_time, last_update_time):
        if d['status'] == 'downloading':
            current_time = time.time()
            if current_time - last_update_time >= 2:  # Update every 2 seconds
                downloaded = d.get('downloaded_bytes', 0)
                total_size = d.get('total_bytes', d.get('total_bytes_estimate', 0))
                speed = d.get('speed', 0)

                if total_size and speed:
                    time_remaining = (total_size - downloaded) / speed
                    percent_complete = downloaded / total_size * 100
                    await message.edit(
                        content=(
                            f"Downloading... {percent_complete:.2f}% complete. "
                            f"Size: {downloaded / 1024 / 1024:.2f}/{total_size / 1024 / 1024:.2f} MB. "
                            f"Speed: {speed / 1024 / 1024:.2f} MB/s. "
                            f"ETA: {time_remaining:.2f} seconds."
                        )
                    )
                last_update_time = current_time

        elif d['status'] == 'finished':
            await message.edit(content="Download completed.")



    async def handle_upload(self, ctx, file_path, info_dict):
        file_size = os.path.getsize(file_path)
        url = f"http://{self.external_ip}:{PORT}/downloads/{os.path.basename(file_path)}"
        if file_size < 25 * 1024 * 1024:
            await ctx.send(content=f"Size: {file_size / 1024 / 1024}mb\n[Link expires in 24 hours]({url})", file=disnake.File(file_path))
        else:
            await ctx.send(f"Size: {file_size / 1024 / 1024}mb\n[Link expires in 24 hours]({url})")

        self.bot.loop.create_task(self.schedule_file_deletion(file_path, 24))

    async def schedule_file_deletion(self, file_path, hours):
        await asyncio.sleep(hours * 3600)
        if os.path.exists(file_path):
            os.remove(file_path)

    async def delete_old_files(self):
        now = datetime.now()
        for root, dirs, files in os.walk(DOWNLOAD_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if (now - file_time).days >= 1:
                    os.remove(file_path)

    @tasks.loop(hours=1)
    async def cleanup(self):
        await self.delete_old_files()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

def setup(bot):
    bot.add_cog(YouTubeDownloader(bot))

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
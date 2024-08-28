import disnake
from disnake.ext import commands, tasks
import yt_dlp
import os
import time
import asyncio
from datetime import datetime
from flask import Flask, send_from_directory, abort, render_template
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

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
        self.last_update_time = 0
        
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
        await ctx.response.defer()
        try:
            # Set initial format options based on user selection
            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title).30s.%(ext)s'),
                'restrictfilenames': True,
                'noplaylist': True,
                'progress_hooks': [lambda d: self.progress_hook(d, ctx)]  # Add the progress hook
            }

            # Run yt-dlp in a separate thread
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                await loop.run_in_executor(pool, self.run_yt_dlp, ydl_opts, url, option, quality, ctx, DOWNLOAD_FOLDER)

            await ctx.edit_original_response(content="Download completed.")
    
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    def run_yt_dlp(self, ydl_opts, url, option, quality, ctx, file_path):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [info_dict])

            best_format = None

            if quality == "lowest available":
                best_format = min(
                    (f for f in formats if f.get('ext') == 'mp4' or option == "audio"),
                    key=lambda f: f.get('filesize', float('inf')),
                    default=None
                )
            elif quality == "highest":
                best_format = max(
                    (f for f in formats if f.get('ext') == 'mp4' or option == "audio"),
                    key=lambda f: f.get('filesize', float('-inf')),
                    default=None
                )
            elif quality == "regular":
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
            self.handle_upload(ctx, file_path, info_dict)

            return info_dict

    def progress_hook(self, d, ctx):
        current_time = time.time()
        if current_time - self.last_update_time < 1:
            return  # Skip update if less than 1 second has passed
        self.last_update_time = current_time

        if d['status'] == 'downloading':
            percent = d['_percent_str'].strip()
            speed = d['_speed_str'].strip()
            eta = d['eta'] if d['eta'] else "N/A"
            asyncio.run_coroutine_threadsafe(
                ctx.edit_original_response(content=f"Downloading... {percent} at {speed} ETA: {eta}s"), 
                self.bot.loop
            )

    def handle_upload(self, ctx, file_path, info_dict):
        file_size = os.path.getsize(file_path)
        url = f"http://{self.external_ip}:{PORT}/downloads/{os.path.basename(file_path)}"
        if file_size < 25 * 1024 * 1024:
            self.bot.loop.create_task(ctx.send(content=f"Size: {file_size / 1024 / 1024:.2f}mb\n[Link expires in 24 hours]({url})", file=disnake.File(file_path)))
        else:
            self.bot.loop.create_task(ctx.send(f"Size: {file_size / 1024 / 1024:.2f}mb\n[Link expires in 24 hours]({url})"))

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

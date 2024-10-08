import disnake
from disnake.ext import commands, tasks
import yt_dlp
import os
import asyncio
from datetime import datetime
from flask import Flask, send_from_directory, abort, render_template
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

# Configuration
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
PORT = 8129

flask_app = Flask(__name__)

@flask_app.route('/downloads/<file_ID>')
def download_file(file_ID):
    return render_template('index.html', file_ID=file_ID)

@flask_app.route('/media/<file_ID>')
def serve_file(file_ID):
    try:
        return send_from_directory(DOWNLOAD_FOLDER, file_ID, as_attachment=True)
    except FileNotFoundError:
        return render_template('404.html'), 404

def run_flask_app():
    flask_app.run(port=PORT, use_reloader=False, host='0.0.0.0', use_evalex=False)

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
        type: str = commands.Param(choices=["video+audio", "audio"], default="video+audio")
    ):
        await ctx.response.defer()
        try:
            # Set initial format options based on user selection
            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title).30s.%(ext)s'),
                'restrictfilenames': True,
                'noplaylist': True,
                'cookiefile': 'cookies.txt'  # Add the cookies file
                # 'extractor_args': {  # Add extractor arguments for YouTube
                #     'youtube': {
                #         'player-client': 'web,default',
                #         'po_token': 'web+doireallyneedthis'
                #     }
                # }
            }
            # Run yt-dlp in a separate thread
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                await loop.run_in_executor(pool, self.run_yt_dlp, ydl_opts, url, type, ctx)

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    def run_yt_dlp(self, ydl_opts, url, type, ctx):
        if type == "audio":
            format_string = "ba[ext=m4a]/ba"
        else:
            format_string = "b[height<=1080]/b"
        # Add format string to yt-dlp options
        ydl_opts['format'] = format_string

        # Use yt-dlp to extract and download the content
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file_path = ydl.prepare_filename(info_dict)

            # Handle file upload or further processing
            self.handle_upload(ctx, downloaded_file_path, info_dict)

        return info_dict


    def handle_upload(self, ctx, file_path, info_dict):
        file_size = os.path.getsize(file_path)
        url = f"http://{self.external_ip}:{PORT}/downloads/{os.path.basename(file_path)}"
        if file_size < 25 * 1024 * 1024:
            self.bot.loop.create_task(ctx.send(content=f"Size: {file_size / 1024 / 1024:.2f}mb\n[Link expires in 1 hour]({url})", file=disnake.File(file_path)))
        else:
            self.bot.loop.create_task(ctx.send(f"Size: {file_size / 1024 / 1024:.2f}mb\n[Link expires in 1 hour]({url})"))

        self.bot.loop.create_task(self.schedule_file_deletion(file_path, 1))

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

import disnake
from disnake.ext import commands, tasks
import yt_dlp
import os
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
    flask_app.run(port=PORT, use_reloader=False)  # use_reloader=False to prevent Flask from restarting the app

class YouTubeDownloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup.start()
        self.external_ip = "smol-ash.happyllama25.net"  # Set this to your server's external IP or domain
        
        # Start Flask app in a separate thread
        flask_thread = Thread(target=run_flask_app)
        flask_thread.start()

    @commands.slash_command()
    async def download(self, ctx, url: str, option: str = "video+audio"):
        await ctx.send(f"Starting download for {url} with option {option}")

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [info_dict])

            best_format = None
            for f in formats:
                if f.get('filesize') and f['filesize'] < 25 * 1024 * 1024 and f.get('ext') == 'mp4':
                    best_format = f['format_id']
                    break
            if not best_format:
                best_format = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

            ydl_opts['format'] = best_format
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            await self.handle_upload(ctx, file_path, info_dict)

    async def handle_upload(self, ctx, file_path, info_dict):
        file_size = os.path.getsize(file_path)
        url = f"http://{self.external_ip}:{PORT}/downloads/{os.path.basename(file_path)}"
        if file_size < 25 * 1024 * 1024:
            await ctx.send(content=f"{url}", file=disnake.File(file_path))
        else:
            await ctx.send(f"[Click here to download the file]({url})")

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

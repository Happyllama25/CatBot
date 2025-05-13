from disnake.ext import commands
from elevenlabs import Voice
from elevenlabs.client import AsyncElevenLabs
import disnake
import asyncio
import os
import pyttsx3
from asyncio import Lock, Queue, get_event_loop
from functools import partial

client = AsyncElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))

class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_threads = {}
        self.voice_locks = {}
        self.message_queues = {}
        self.thread_creators = {}
        # track fallback to local TTS per guild
        self.use_local = {}

    @commands.slash_command(name="speak", description="Start a TTS session in a voice channel")
    async def speak(self, ctx):
        await ctx.response.defer()

        if hasattr(ctx, 'voice_error'):
            await ctx.edit_original_response(content=ctx.voice_error)
            return

        channel = ctx.author.voice.channel
        thread_name = f"TTS-{channel.name}"

        if thread_name in self.active_threads:
            await ctx.edit_original_response(content="A TTS thread is already active.")
            return

        voice_client = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client is None:
            voice_client = await channel.connect()

        # reset fallback for this session
        self.use_local[ctx.guild.id] = False

        initial_message = await ctx.channel.send(
            content=(f'{ctx.author.mention}\n'
                     f'Voice Channel: {channel.name}\n\n'
                     'Use `$stop` or disconnect to end the session.')
        )

        thread = await ctx.channel.create_thread(
            name=thread_name,
            message=initial_message,
            auto_archive_duration=60
        )

        self.active_threads[thread_name] = thread
        self.voice_locks[ctx.guild.id] = Lock()
        self.message_queues[ctx.guild.id] = Queue()
        self.thread_creators[thread.id] = ctx.author.id

        await ctx.edit_original_response(content=f"TTS session started! Use the thread <#{thread.id}> to send messages.")

        # spawn queue processor and monitor
        self.bot.loop.create_task(self.process_queue(voice_client, thread, ctx.guild.id))
        self.bot.loop.create_task(self.monitor_creator(ctx.guild, ctx.author, thread))

        try:
            while True:
                msg = await self.bot.wait_for(
                    'message', check=lambda m: m.channel.id == thread.id, timeout=None
                )
                if msg.author == self.bot.user:
                    continue
                if msg.content.lower() == "$stop":
                    await thread.send("Stopping TTS session and disconnecting.")
                    break
                await self.message_queues[ctx.guild.id].put(msg.content)
        except Exception as e:
            await thread.send(f"An error occurred: {e}")

        await voice_client.disconnect()
        await thread.edit(archived=True, locked=True)
        # cleanup
        del self.active_threads[thread_name]
        del self.voice_locks[ctx.guild.id]
        del self.message_queues[ctx.guild.id]
        del self.thread_creators[thread.id]
        del self.use_local[ctx.guild.id]

    async def process_queue(self, voice_client, thread, guild_id):
        # ensure output folder
        output_folder = 'tts_output'
        os.makedirs(output_folder, exist_ok=True)

        # define file names
        api_file = os.path.join(output_folder, f"{guild_id}.mp3")
        local_file = os.path.join(output_folder, f"{guild_id}.wav")

        while True:
            text = await self.message_queues[guild_id].get()
            async with self.voice_locks[guild_id]:
                # decide target file
                target = api_file if not self.use_local.get(guild_id, False) else local_file
                try:
                    if not self.use_local.get(guild_id, False):
                        # stream cloud TTS directly to mp3
                        gen = await client.generate(
                            text=text,
                            voice=Voice(voice_id="pNInz6obpgDQGcFmaJgB"),
                            model="eleven_multilingual_v2",
                            stream=True
                        )
                        with open(api_file, 'wb') as f:
                            async for chunk in gen:
                                f.write(chunk)
                    else:
                        # run local wav TTS
                        await self.run_local_tts(text, local_file)

                    # play file via ffmpeg
                    source = disnake.FFmpegPCMAudio(target)
                    voice_client.play(source, after=lambda e: print(f"Player error: {e}"))
                    while voice_client.is_playing():
                        await asyncio.sleep(0.5)

                except Exception as e:
                    # on first cloud failure, switch to local and retry once
                    if not self.use_local.get(guild_id, False):
                        self.use_local[guild_id] = True
                        await thread.send("⚠️ ElevenLabs API failed — switching to local TTS.")
                        try:
                            await self.run_local_tts(text, local_file)
                            source = disnake.FFmpegPCMAudio(local_file)
                            voice_client.play(source)
                            while voice_client.is_playing():
                                await asyncio.sleep(0.5)
                        except Exception as le:
                            await thread.send(f"Local TTS also failed: {le}")
                    else:
                        await thread.send(f"TTS error: {e}")

                finally:
                    # cleanup any generated files
                    for f in (api_file, local_file):
                        try:
                            if os.path.exists(f):
                                os.remove(f)
                        except OSError:
                            pass

    async def run_local_tts(self, text: str, outfile: str):
        """
        Synthesize `text` to `outfile` (WAV) using pyttsx3 in a thread-pool.
        """
        loop = get_event_loop()
        await loop.run_in_executor(None, partial(self._pyttsx3_synth, text, outfile))

    def _pyttsx3_synth(self, text: str, outfile: str):
        engine = pyttsx3.init()
        # choose a natural English voice if available
        voices = engine.getProperty('voices')
        en = next((v for v in voices if 'english' in v.name.lower()), None)
        if en:
            engine.setProperty('voice', en.id)
        # adjust speech properties
        engine.setProperty('rate', 130)
        engine.setProperty('volume', 1.0)
        try:
            engine.setProperty('pitch', 70)
        except Exception:
            pass
        engine.save_to_file(text, outfile)
        engine.runAndWait()
        engine.stop()

    async def monitor_creator(self, guild, creator, thread):
        try:
            while True:
                if not creator.voice or creator.voice.channel.guild.id != guild.id:
                    await thread.send(
                        "Thread parent left; archiving and disconnecting."
                    )
                    await thread.edit(archived=True, locked=True)
                    vc = disnake.utils.get(self.bot.voice_clients, guild=guild)
                    if vc:
                        await vc.disconnect()
                    break
                await asyncio.sleep(5)
        except Exception as e:
            await thread.send(f"Monitoring error: {e}")

    @speak.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.author.voice:
            ch = ctx.author.voice.channel
            vc = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if vc is None:
                await ch.connect()
            elif vc.channel != ch:
                await vc.move_to(ch)
        else:
            ctx.voice_error = "You are not connected to a voice channel."


def setup(bot):
    bot.add_cog(TTSCog(bot))

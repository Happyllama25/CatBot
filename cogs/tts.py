from disnake.ext import commands
from elevenlabs import Voice
from elevenlabs.client import AsyncElevenLabs
import disnake
import asyncio
import os
from asyncio import Lock, Queue

client = AsyncElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))

class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_threads = {}
        self.voice_locks = {}
        self.message_queues = {}
        self.thread_creators = {}

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

        voice_channel_name = channel.name
        initial_message = await ctx.channel.send(
            content=f'{ctx.author.mention}\nVoice Channel: {voice_channel_name}\n\nUse `$stop` or disconnect from <#{channel.id}> to end the session.'
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

        try:
            # Start the TTS processing loop
            self.bot.loop.create_task(self.process_queue(voice_client, thread, ctx.guild.id))
            self.bot.loop.create_task(self.monitor_creator(ctx.guild, ctx.author, thread))

            while True:
                msg = await self.bot.wait_for('message', check=lambda m: m.channel.id == thread.id, timeout=None)

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
        del self.active_threads[thread_name]
        del self.voice_locks[ctx.guild.id]
        del self.message_queues[ctx.guild.id]
        del self.thread_creators[thread.id]

    async def process_queue(self, voice_client, thread, guild_id):
        output_folder = 'tts_output'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_file_path = os.path.join(output_folder, f"tts_output.mp3")

        while True:
            try:
                message = await self.message_queues[guild_id].get()
                async with self.voice_locks[guild_id]:
                    try:
                        # Generate TTS audio
                        audio_generator = await client.generate(
                            text=message,
                            voice=Voice(voice_id="pNInz6obpgDQGcFmaJgB"),
                            model="eleven_multilingual_v2",
                            stream=True
                        )

                        with open(output_file_path, 'wb') as file:
                            async for audio_data in audio_generator:
                                file.write(audio_data)

                        source = disnake.FFmpegPCMAudio(output_file_path)
                        voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

                        while voice_client.is_playing():
                            await asyncio.sleep(1)

                    except Exception as e:
                        await thread.send(f"Error processing message: {e}")
                    finally:
                        if os.path.exists(output_file_path):
                            os.remove(output_file_path)

            except asyncio.CancelledError:
                break

    async def monitor_creator(self, guild, creator, thread):
        try:
            while True:
                if not creator.voice or creator.voice.channel.guild.id != guild.id:
                    await thread.send("Thread parent left the channel, im gonna go cry now\n(archiving and locking the thread)")
                    await thread.edit(archived=True, locked=True)
                    voice_client = disnake.utils.get(self.bot.voice_clients, guild=guild)
                    if voice_client:
                        await voice_client.disconnect()
                    break
                await asyncio.sleep(5)
        except Exception as e:
            await thread.send(f"An error occurred in monitoring\nim sowwy 🥺\n{e}")

    @speak.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice_client is None:
                await channel.connect()
            elif voice_client.channel != channel:
                await voice_client.move_to(channel)
        else:
            ctx.voice_error = "You are not connected to a voice channel."

def setup(bot):
    bot.add_cog(TTSCog(bot))

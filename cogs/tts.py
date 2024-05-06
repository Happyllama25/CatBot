from disnake.ext import commands
from elevenlabs.client import AsyncElevenLabs
import disnake
import asyncio
import os

client = AsyncElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))


class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="speak", description="Speak a message in a voice channel")
    async def speak(self, ctx, message: str):
        await ctx.response.defer()

        if hasattr(ctx, 'voice_error'):
            await ctx.edit_original_response(content=ctx.voice_error)
            return

        voice_client = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice_client.is_playing():
            await ctx.edit_original_response(content="I am already speaking in the voice channel.")
            return

        output_folder = 'tts_output'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_file_path = os.path.join(output_folder, f"tts_output.mp3")

        try:
            # Await the coroutine to get the async generator
            audio_generator = await client.generate(
                text=message,
                voice="Adam",
                model="eleven_multilingual_v2",
                stream=True
            )

            with open(output_file_path, 'wb') as file:
                async for audio_data in audio_generator:
                    file.write(audio_data)  # Write each chunk to the file
        except Exception as e:
            await ctx.edit_original_response(content=f"An error occurred: {e}")
            return

        source = disnake.FFmpegPCMAudio(output_file_path)
        voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        while voice_client.is_playing():
            await asyncio.sleep(1)
        
        await voice_client.disconnect()
        await ctx.edit_original_response(file=disnake.File(output_file_path))
        os.remove(output_file_path)

    @speak.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice_client is None:
                await channel.connect()
            elif voice_client.is_playing():
                # Set a flag in the context instead of sending a response
                ctx.voice_error = "I'm already speaking. Please wait until I'm finished."
            elif voice_client.channel != channel:
                await voice_client.move_to(channel)
        else:
            # Set a flag in the context instead of sending a response
            ctx.voice_error = "You are not connected to a voice channel."

def setup(bot):
    bot.add_cog(TTSCog(bot))

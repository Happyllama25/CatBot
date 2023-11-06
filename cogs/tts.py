from disnake.ext import commands
from elevenlabs import generate
import disnake
import asyncio
import os

class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="speak", description="Speak a message in a voice channel")
    async def speak(self, ctx, message: str):
        # Defer the response
        await ctx.response.defer()

        # Check for pre-invocation errors set by 'ensure_voice' before_invoke hook
        if hasattr(ctx, 'voice_error'):
            await ctx.edit_original_response(content=ctx.voice_error)
            return

        voice_client = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)

        # No need to check if voice_client is None because 'ensure_voice' already did

        # Check if the bot is already playing audio
        if voice_client.is_playing():
            await ctx.edit_original_response(content="I am already speaking in the voice channel.")
            return

        # Generate the audio data
        await ctx.edit_original_response(content="Generating audio...")
        audio_data = generate(
            text=f'{message}',
            voice="Dorothy",
            model="eleven_multilingual_v1"
        )

        # Specify the filename for the output file
        output_file_path = 'output/tts_output.mp3'

        # Write the audio data to the file
        try:
            with open(output_file_path, 'wb') as audio_file:
                audio_file.write(audio_data)
        except Exception as e:
            await ctx.edit_original_response(content=f"Failed to generate audio file: {e}")
            return

        # Send the audio file to the channel and play it
        try:
            source = disnake.FFmpegPCMAudio(output_file_path)
            voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.edit_original_response(file=disnake.File(output_file_path))


            # Wait for the audio to play
            while voice_client.is_playing():
                await asyncio.sleep(1)
            # Disconnect after the bot has played the TTS message
            await asyncio.sleep(1)
            await voice_client.disconnect()
        except Exception as e:
            await ctx.edit_original_response(content=f"An error occurred: {e}")
        finally:
            # Delete the output file
            if os.path.exists(output_file_path):
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

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from disnake.ext import commands
from enum import Enum
from pydub import AudioSegment
import os
import disnake

load_dotenv('.env')

class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_TTS_KEY"),
            region="eastus")

    class Voices(str, Enum):
        voice1 = "en-US-AriaNeural"

    @commands.slash_command(description="Join a voice channel and speak the text")
    async def speak(self, inter, voice:Voices, text: str):
        await inter.response.defer(ephemeral=False)
        voice_channel = inter.author.voice
        if voice_channel is None:
            await inter.edit_original_response("You are not connected to any voice channel.")
            return
        voice_channel = inter.author.voice.channel
        print(f'user is in voice channel {voice_channel.name}')
        try:
            print(f"Connecting to voice channel: {voice_channel.name}")
            vc = await voice_channel.connect()
            print(f"Connected to voice channel: {voice_channel.name}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            
        print(f"Setting voice to: {voice}")
        self.speech_config.speech_synthesis_voice_name = voice
        print(f"Voice set to: {voice}")
        print(f"Synthesizing audio for text: {text}")
        # TTS with Azure
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)
        result = speech_synthesizer.speak_text_async(text).get()
        print(f"Speech synthesis result: {result.reason}")
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # convert mp3 file to wav as disnake's voice client uses ffmpeg to play audio, which requires the file to be in .wav format
            stream = speechsdk.AudioDataStream(result)
            audio_file = "output.wav"
            stream.save_to_wav_file(audio_file)
            vc.play(disnake.FFmpegPCMAudio(source=audio_file))
            inter.edit_original_response("Speaking...")
            while vc.is_playing():
                continue
            await vc.disconnect()
            inter.edit_original_response("Done speaking.")

            # send the audio file if it's less than 25MB
            file_size = os.path.getsize(audio_file) / (1024 * 1024)  # get file size in MB
            if file_size <= 25:
                with open(audio_file, 'rb') as f:
                    await inter.edit_original_response("Here is the audio file", file=disnake.File(f, filename="output.wav"))
            else:
                await inter.edit_original_response("The synthesized audio file is too large to upload.")

            os.remove(audio_file)
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
            await vc.disconnect()
            await inter.response.send_message(f"An error occurred: {cancellation_details.reason}")
            
def setup(bot):
    bot.add_cog(TTS(bot))

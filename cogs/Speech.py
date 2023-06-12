import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from disnake.ext import commands
from voices import voices
import os
import disnake

load_dotenv('.env')

class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_TTS_KEY"),
            region="eastus")


    async def autocomp_voices(inter: disnake.ApplicationCommandInteraction, user_input: str):
        return [v for v in voices if user_input.lower() in v]



    @commands.slash_command(description="Join a voice channel and speak the text")
    async def speak(self, inter, text: str, voice: str = commands.Param(autocomplete=autocomp_voices)):
        await inter.send(f"Setting voice to: {voice}")
        voice_channel = inter.author.voice.channel
        if voice_channel is None:
            await inter.edit_original_response("You are not connected to any voice channel. Stopping.")
            return
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
        audio_file = "audio.mp3"
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)
        result = speech_synthesizer.speak_text_async(text).get()
        print(f"Speech synthesis result: {result.reason}")

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # Save synthesized audio to a WAV file
            stream = speechsdk.AudioDataStream(result)
            audio_file = f"{inter.author}_output.wav"
            stream.save_to_wav_file(audio_file)

            # Play the audio file
            vc.play(disnake.FFmpegPCMAudio(executable="ffmpeg", source=audio_file))

            # convert mp3 file to wav as disnake's voice client uses ffmpeg to play audio, which requires the file to be in .wav format
            # stream = speechsdk.AudioDataStream(result)
            # audio_file = "output.mp3"
            # stream.save_to_file(audio_file)
            # vc.play(disnake.FFmpegPCMAudio(source=audio_file)) # type: ignore
            await inter.edit_original_response("Speaking...")
            while vc.is_playing():
                continue
            await vc.disconnect()
            await inter.edit_original_response("Done speaking.")

            # send the audio file if it's less than 25MB
            file_size = os.path.getsize(audio_file) / (1024 * 1024)  # get file size in MB
            if file_size <= 24:
                with open(audio_file, 'rb') as f:
                    await inter.edit_original_response("Here is the synthesized audio:", file=disnake.File(f, "audio.mp3"))
            else:
                await inter.edit_original_response("The audio file is too large to upload.")

            try:
                os.remove(audio_file)
            except FileNotFoundError:
                pass
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
            await vc.disconnect()
            await inter.edit_original_response(f"An error occurred: {cancellation_details.reason}")
            
def setup(bot):
    bot.add_cog(TTS(bot))

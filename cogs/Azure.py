import azure.cognitiveservices.speech as speechsdk
import azure.ai.vision as visionsdk
from dotenv import load_dotenv
from disnake.ext import commands
from voices import voices
import os
from typing import Optional
import disnake

load_dotenv('.env')

class azure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_TTS_KEY"),
            region="eastus")

    @commands.slash_command(name="identify", description="Identify components of an image with Azure")
    async def identify(self, inter: disnake.ApplicationCommandInteraction, file: Optional[disnake.Attachment] = None, url: Optional[str] = None, text:bool = commands.Param(default=False, description="Analyze text? (if a lot will make message big)")):
        if file is None and url is None:
            await inter.send("Please provide a url or attachment")
            return
        if file is not None and url is not None:
            await inter.send("Please provide a url or attachment, not both")
            return
        if file:
            url = file.url
        await inter.response.defer()
        service_options = visionsdk.VisionServiceOptions('https://catbot-eyes.cognitiveservices.azure.com/',
                                                os.getenv("VISION_API_KEY"))

        vision_source = visionsdk.VisionSource(
            url=url)

        analysis_options = visionsdk.ImageAnalysisOptions()

        if text:
            analysis_options.features = (
                visionsdk.ImageAnalysisFeature.CAPTION |
                visionsdk.ImageAnalysisFeature.TEXT
            )
        else:
            analysis_options.features = (
                visionsdk.ImageAnalysisFeature.CAPTION
            )

        analysis_options.language = "en"
        # analysis_options.gender_neutral_caption = True

        image_analyzer = visionsdk.ImageAnalyzer(service_options, vision_source, analysis_options)

        result = image_analyzer.analyze()

        if result.reason == visionsdk.ImageAnalysisResultReason.ANALYZED:

            if result.caption is not None:
                message = f"{url}\n\n{result.caption.content.capitalize()}\nConfidence {result.caption.confidence*100:.4f}%\n\n"

            if result.text is not None:
                message += "Text:\n"
                for line in result.text.lines:
                    message += f"Line: '{line.content}'\n"
                await inter.edit_original_response(message[:2000])
            else:
                await inter.edit_original_response(message)

        else:

            error_details = visionsdk.ImageAnalysisErrorDetails.from_result(result)
            message = "```diff\nAnalysis failed.\n\n"
            message += f"-Error reason: {error_details.reason}\n"
            message += f"-Error code: {error_details.error_code}\n"
            message += f"-Error message: {error_details.message}\n```"

    async def autocomp_voices(inter: disnake.ApplicationCommandInteraction, user_input: str): #type: ignore
        return [v for v in voices if user_input.lower() in v]

    @commands.slash_command(description="Join a voice channel and speak the text")
    async def speak(self, inter, text: str, voice: str = commands.Param(autocomplete=autocomp_voices)):
        await inter.send(f"Setting voice to: {voice}")
        voice_channel = inter.author.voice.channel
        if voice_channel is None:
            await inter.edit_original_response("You are not connected to any voice channel. Stopping.")
            return

        print(f'user is in voice channel {voice_channel.name}')

        # Check if bot is already in a voice channel
        for vc in self.bot.voice_clients:
            if vc.guild == inter.guild:
                if vc.channel == voice_channel:
                    print(f"Already connected to voice channel: {voice_channel.name}")
                else:
                    await vc.move_to(voice_channel)
                    print(f"Moved to voice channel: {voice_channel.name}")
                break
        else:  # Bot is not connected to any voice channel in the server
            try:
                print(f"Connecting to voice channel: {voice_channel.name}")
                vc = await voice_channel.connect()
                print(f"Connected to voice channel: {voice_channel.name}")
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                return

        print(f"Connected to voice channel: {voice_channel.name}")
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
            # convert mp3 file to wav as disnake's voice client uses ffmpeg to play audio, which requires the file to be in .wav format
            stream = speechsdk.AudioDataStream(result)
            audio_file = "output.mp3"
            stream.save_to_wav_file(audio_file)
            vc.play(disnake.FFmpegPCMAudio(source=audio_file))
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
    bot.add_cog(azure(bot))

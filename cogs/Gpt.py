import openai
import disnake
from disnake.ext import commands
import os
import requests
from dotenv import load_dotenv
load_dotenv('.env')
openai.organization = "org-AyvZFGJwqixw5tj5lgq4XHE3"
openai.api_key = os.getenv("OPENAI_API_KEY")


class Gpt(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='gpt', description="ChatGPT integration - AI response")
    async def GPT(self, ctx, *, message: str):
        await ctx.response.defer(ephemeral=False)
        conversation = [{"role": "user", "content": f"{message}"}]

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=conversation)

        response = completion.choices[0].message['content']
        # If the response is too long, send in multiple pieces, otherwise send it all in one message
        if len(response) <= 2000:
            await ctx.edit_original_response(response)
        else:
            try:  # Try to create a new thread, if the thread is already created and command was called from inside the thread, send it normally
                if isinstance(ctx.channel, disnake.Thread):
                    await ctx.edit_original_response('Response too long, sending in chunks...')
                    thread = ctx.channel  # Create a thread to keep all related messages together neatly
                    chunks = [response[i:i+2000]
                              for i in range(0, len(response), 2000)]
                    for chunk in chunks:
                        await thread.send(chunk)
                    # # Add the response to the saved conversation
                    # conversation.append(
                    #     {"role": "system", "content": response}) ---HERE!!!!

                else:  # Create the thread and send messages in it
                    message = await ctx.edit_original_response('Response too long, sending in chunks...')
                    thread_name = f'{ctx.author.name}\'s GPT Thread'
                    thread = await message.create_thread(name=thread_name, auto_archive_duration=60)
                    chunks = [response[i:i+2000]
                              for i in range(0, len(response), 2000)]
                    for chunk in chunks:
                        await thread.send(chunk)
                    # # Add the response to the saved conversation
                    # conversation.append(
                    #     {"role": "system", "content": response}) ---HERE!!!!

            except disnake.errors.HTTPException as eror:
                if eror.code == 50024:
                    await ctx.edit_original_response('Cannot create a thread inside of an existing thread')
                else:
                    await ctx.edit_original_response('Oops! Something went wrong! Please try again. (this is extremely unlikely to happen, if you are anthony please **K**eep **Y**ourself **S**afe)')

    @commands.slash_command(name='imagine', description="OpenAI DALL-E image generation")
    async def imagine(self, ctx, prompt: str):
        await ctx.response.defer(ephemeral=False)

        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512",
            )
        except openai.InvalidRequestError as error:
            if "safety system" in str(error):
                await ctx.edit_original_response(content="Your prompt got flagged.")

                # Perform a moderation check on the prompt
                moderation_response = openai.Moderation.create(input=prompt)
                # Check if the prompt triggered the OpenAI safety system
                moderation_triggered = [category for category, value in moderation_response.results[0].categories.items() if value]
                if moderation_triggered:
                    return await ctx.edit_original_response(content=f"Your prompt got flagged for: ```{', '.join(moderation_triggered)}```")
                else:
                    return await ctx.edit_original_response(content="Your prompt got flagged but didnt specify a topic.")
            else:
                return await ctx.edit_original_response(content=f"An error occurred while generating the image.\n\n||{error}||")

        image_url = response['data'][0]['url']  # type: ignore
        # Create the "generated images" directory if it doesn't exist
        if not os.path.exists("generated-images"):
            os.makedirs("generated-images")
        
        # Download the image and save it to disk
        image_data = requests.get(image_url, timeout=20).content
        image_filename = f"{ctx.author.name}_{prompt}.png"
        image_path = os.path.join("generated-images", image_filename[:35])
        try:
            with open(image_path, 'wb') as f:
                f.write(image_data)
        except OSError:
            return await ctx.edit_original_response(content=f"An error occurred while saving the image. This will expire in 2 hours. (you should save it)\n{image_url}")

        # Send the image as an attachment
        await ctx.edit_original_response(file=disnake.File(image_path, description=f"Prompt: {prompt}"))


def setup(bot):
    bot.add_cog(Gpt(bot))

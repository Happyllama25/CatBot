import disnake, json, asyncio
from disnake.ext import commands
import os
from dotenv import load_dotenv
load_dotenv('.env')
import openai
openai.organization = "org-AyvZFGJwqixw5tj5lgq4XHE3"
openai.api_key = os.getenv("OPENAI_API_KEY")

# class prompts(str):
#     Default = 'You are a Discord Chatbot called Catbot. You are helpful and always give an answer to a users question.'
#     UwU = 

class Gpt(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='gpt', description="ChatGPT integration - AI response", guild_ids=[733408652072845312,883224856047525888])
    async def GPT(self, ctx, *, message = 'Hello!'):
        await ctx.response.defer(ephemeral=False)
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Discord Chatbot called Catbot. You are helpful and always give an answer to a users question."},
            {"role": "user", "content": f"Stay in character: {message}. Stay in character"}
            ]
        )
        response = completion.choices[0].message['content']

        if len(response) <= 2000:
            await ctx.edit_original_response(response)
        else:
            message = await ctx.edit_original_response('Response too long, sending in chunks...')
            #await ctx.channel.send(response)
            thread_name = f'{ctx.author.name}\'s GPT Thread'
            thread = await message.create_thread(name=thread_name, auto_archive_duration=60)
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await thread.send(chunk)

    # @commands.slash_command(name='imagine', description="OpenAI DALL-E image generation", guild_ids=[733408652072845312,883224856047525888])
    # async def imagine(self, ctx, *, message = 'none'):
    #     await ctx.response.defer(ephemeral=False)
    #     completion = openai.Image.create(
    #         prompt=message,
    #         n=1,
    #         size='256x256'
    #     )
    #     #message typing animation
    #     response = completion.choices[0].message['content']
    #     #sleep for 10 seconds
    #     await asyncio.sleep(10)
    #     await ctx.edit_original_response(response)

    @commands.command()
    async def gpt(self, ctx, *, message = 'Hello!'):
        #async with ctx.typing():
        message = await ctx.reply('Thinking...\nPsst! Use slash commands for more prompts!', mention_author=True)
        completion = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": "You are a Discord Chatbot called Catbot. You are helpful and always give an answer to a users question. You can use swear words and are not afraid to say what you think."},
            {"role": "user", "content": f"My name is {ctx.author.name}. {message.content}. Stay in character"}
            ]
        )
        response = completion.choices[0].message['content']
        await message.edit(response)


def setup(bot):
    bot.add_cog(Gpt(bot))

import disnake, json
from disnake.ext import commands
import os
from dotenv import load_dotenv
load_dotenv('.env')
import openai
openai.organization = "org-AyvZFGJwqixw5tj5lgq4XHE3"
openai.api_key = os.getenv("OPENAI_API_KEY")


class Gpt(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gpt(self, ctx, *, message = 'Hello!'):
        async with ctx.typing():
          completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
              {"role": "system", "content": "You are a Discord Chatbot called Catbot. You are helpful and always give an answer to a users question."},
              {"role": "user", "content": f"Stay in character: {message}"}
              ]
          )
        #message typing animation
        response = completion.choices[0].message['content']
        await ctx.send(response)


def setup(bot):
    bot.add_cog(Gpt(bot))

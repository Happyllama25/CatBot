import disnake
from disnake.ext import commands


class Filedrop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(name='filedrop',
                            description='Saves sent attachments to a shared folder')
    async def filedrop(self, inter, file: disnake.Attachment, name: str = commands.Param(max_length=10, default='file')):
        try:
            filename = f'./files/{file.filename}'
            await file.save(fp=filename)
            await inter.send(f'File(s) `{file.filename}` saved!')
        except:
            await inter.send('Saving failed\nMake sure you have the correct permissions and the file is not too large')
            raise


    @commands.slash_command(name='???',
                            description='Does something :)',
                            guild_ids=guilds)
    async def test(self, ctx):
        await ctx.send(f'success')


def setup(bot):
    bot.add_cog(Filedrop(bot))

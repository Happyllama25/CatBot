import disnake
import qrcode
import json
import random
from datetime import datetime
import os
import sys
from io import BytesIO
from disnake.ext import commands

class Utilities(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        if not os.path.exists("quotes.json"):
            with open("quotes.json", "w") as file:
                json.dump([], file)


    @commands.slash_command(name="suggest", description="Suggest a feature for this bot!")
    async def suggest(self, ctx, message: str = commands.Param(name="suggestion", description="Your suggestion or message for the dev!")):
        owner = await self.bot.fetch_user(self.bot.owner_id)
        if owner:
            await owner.send(f"Suggestion from {ctx.author.mention}: {message}")
            await ctx.send("Your suggestion has been sent to the bot owner!")
        else:
            await ctx.send("Sorry, I couldn't find the bot owner to send your suggestion.")


    @commands.slash_command(
        name="generate_qr",
        description="Generates a QR code from the provided input with Minecraft colors."
    )
    async def generate_qr(self, ctx, 
                        text_or_link: str = commands.Param(name='text-or-link',description="Text or link to convert to QR.", default=None),
                        file: disnake.Attachment = commands.Param(description="Text file to read content from and convert to QR.", default=None),
                        fill_color: str = commands.Param(name='fill-colour',description="Colour of the QR code data.", choices=["dark_red", "red", "gold", "yellow", "dark_green", "green", "aqua", "dark_aqua", "dark_blue", "blue", "light_purple", "dark_purple", "white", "gray", "dark_gray", "black"], default="dark_gray"),
                        back_color: str = commands.Param(name='background-colour',description="Background colour of the QR code. (Cannot be too similar in hue as the Code colour or it won't scan)", choices=["dark_red", "red", "gold", "yellow", "dark_green", "green", "aqua", "dark_aqua", "dark_blue", "blue", "light_purple", "dark_purple", "white", "gray", "dark_gray", "black"], default="white"),
                        pixel_size: int = commands.Param(name='pixel-size',description="Size of each pixel in the QR code.",ge=0, le=100, default=10),
                        error_correction: str = commands.Param(name='error-correction',description="Error correction level of the QR code. (how much can be covered/modified and still have it scan)", choices=["Low", "Medium", "Quartile", "High"], default="Low")
                        ):
        if not text_or_link and not file:
            await ctx.send("u gotta send at least *something* smh... text, link or upload a file to generate a QR code.")
            return
        if text_or_link and file:
            await ctx.send("u can't send text AND a file, pick one. >:(")
            return
        
        colour_mapping = {
            "dark_red": (170, 0, 0),
            "red": (255, 85, 85),
            "gold": (255, 170, 0),
            "yellow": (255, 255, 85),
            "dark_green": (0, 170, 0),
            "green": (85, 255, 85),
            "aqua": (85, 255, 255),
            "dark_aqua": (0, 170, 170),
            "dark_blue": (0, 0, 170),
            "blue": (85, 85, 255),
            "light_purple": (255, 85, 255),
            "dark_purple": (170, 0, 170),
            "white": (255, 255, 255),
            "gray": (170, 170, 170),
            "dark_gray": (85, 85, 85),
            "black": (0, 0, 0)
        }
        error_correction_map = {
            'Low': qrcode.constants.ERROR_CORRECT_L,
            'Medium': qrcode.constants.ERROR_CORRECT_M,
            'Quartile': qrcode.constants.ERROR_CORRECT_Q,
            'High': qrcode.constants.ERROR_CORRECT_H,
        }

        error_correction_value = error_correction_map.get(error_correction, qrcode.constants.ERROR_CORRECT_L)
        try:
            # If file is provided, read its content
            if file:
                try:
                    content = (await file.read()).decode()
                except UnicodeDecodeError:
                    await ctx.send("Uploaded file is not compatible, converting file link instead:")
                    content = file.url
            else:
                content = text_or_link

            # Generate QR code
            qr = qrcode.QRCode(
                error_correction=error_correction_value,
                box_size=pixel_size,
                border=1,
            )
            qr.add_data(content)
            qr.make(fit=True)

            img = qr.make_image(fill=colour_mapping[fill_color], back_color=colour_mapping[back_color])
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)

            await ctx.send(file=disnake.File(buf, filename='qrcode.png'))
        except Exception as error:
            await ctx.send(f"nuh uh: {error}")


        
    @commands.slash_command(name="kys", description="Restarts the bot")
    async def kys(self, ctx):
        await ctx.send("Yes master, whatever you desire\nhttps://tenor.com/view/death-cat-falls-over-gif-17605935280907017193")
        os._exit(0)

    @commands.slash_command(name="info", description="Get server or user info")
    async def info(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member = None):
        if user:
            embed = disnake.Embed(timestamp=datetime.utcnow(), color=disnake.Colour.purple())
            embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.display_avatar.url)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(name="Nickname", value=user.display_name, inline=True)
            embed.add_field(name="Joined Server", value=user.joined_at.strftime("%d %b %Y %H:%M:%S"), inline=True)
            embed.add_field(name="Account Created", value=user.created_at.strftime("%d %b %Y %H:%M:%S"), inline=True)
            embed.add_field(name="Status", value=str(user.status).title(), inline=True)
            activity = "None" if not user.activities else user.activities[0].name
            embed.add_field(name="Activity", value=activity, inline=True)
            embed.add_field(name="Top Role", value=user.top_role.name if user.top_role else "None", inline=True)
            embed.add_field(name="Is Bot", value="Yes" if user.bot else "No", inline=True)
            if user.premium_since:
                embed.add_field(name="Boosting Since", value=user.premium_since.strftime("%d %b %Y %H:%M:%S"), inline=True)
        else:
            embed = disnake.Embed(timestamp=datetime.utcnow(), color=disnake.Colour.blue())
            guild = inter.guild
            embed.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else None)
            embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
            embed.add_field(name="Members", value=str(guild.member_count), inline=True)
            embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
            embed.add_field(name="Created", value=guild.created_at.strftime("%d %b %Y %H:%M:%S"), inline=True)
            embed.add_field(name="Boost Level", value=str(guild.premium_tier), inline=True)
            embed.add_field(name="Boost Count", value=str(guild.premium_subscription_count), inline=True)
            embed.add_field(name="Emojis", value=str(len(guild.emojis)), inline=True)
            embed.add_field(name="Features", value=', '.join(guild.features), inline=False)

        await inter.send(embed=embed)

def setup(bot):
    bot.add_cog(Utilities(bot))
import disnake
import qrcode
import aiohttp
from io import BytesIO
from disnake.ext import commands

class Utilities(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


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

    

def setup(bot):
    bot.add_cog(Utilities(bot))

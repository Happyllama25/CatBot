import disnake
import json
import random
import sqlite3
from datetime import datetime
import os
import warnings
from typing import Optional
from disnake.ext import commands

DB_PATH = 'quotes.db'

class Quotes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        if not os.path.exists("quotes.json"):
            with open("quotes.json", "w") as file:
                json.dump([], file)
        # Initialize the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                rowid INTEGER PRIMARY KEY,
                author INTEGER,
                author_nickname TEXT,
                quoter INTEGER,
                quoter_nickname TEXT,
            content TEXT,
            timestamp INTEGER,
            message_id INTEGER,
            channel_id INTEGER,
            tick INTEGER DEFAULT 0
        );""")
        conn.commit()
        conn.close()


    @commands.message_command(name="quote")
    async def quote(self, inter: disnake.ApplicationCommandInteraction, message: disnake.Message):
        try:
            message = await inter.channel.fetch_message(message.id)
        except disnake.NotFound:
            await inter.response.send_message("Message not found.")
            return
        except disnake.Forbidden:
            await inter.response.send_message("I don't have permission to fetch that message. (can I read that channel?)")
            return

        content = message.content
        lines = content.splitlines()

        prefixed_lines = []
        for line in lines:
            #if an empty line is encountered, make it a new line with \n
            if line.strip() == "":
                prefixed_lines.append("\n")
                continue
            prefixed_line = f"-# {line}"
            prefixed_lines.append(prefixed_line)

        prefixed = "\n".join(prefixed_lines)

        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO quotes (
                        author,
                        author_nickname,
                        quoter,
                        quoter_nickname,
                        content,
                        timestamp,
                        message_id,
                        channel_id,
                        tick
                        )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(message.author.id),
                str(message.author.display_name),
                int(inter.author.id),
                str(inter.author.display_name),
                str(message.content),
                int(message.created_at.timestamp()),
                int(message.id),
                int(message.channel.id),
                0
            ))
            conn.commit()
        except Exception as e:
            _message = f'errm... something broke..\n#- {e}\n**runs away**'
            print(f"⚠️⚠️ Error: {e}")
            await inter.response.send_message(content=_message)
        finally:
            conn.close()

        # reply
        _message = (
            f'Quoted!\n'
            f'{prefixed[:1900]}\n'
            f'-# {message.jump_url}'
        )
        await inter.response.send_message(content=_message[:2000])

    @commands.slash_command(name="recall_quote", description="Get a quote from archive. Right-click a message -> apps -> quote to add.")
    async def recall_quote(self, inter: disnake.ApplicationCommandInteraction): #, user: Optional[disnake.User] = None
        # Load the quotes
        reset_quotes = False
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # if user:
        #     rows = cursor.execute("""SELECT rowid, author, author_nickname, quoter, quoter_nickname, content, timestamp, 
        #                           message_id, channel_id FROM quotes WHERE author = ? AND tick = 0""", (int(user.id),))
        # else:
        rows = cursor.execute("""
            SELECT rowid, author, author_nickname, quoter, quoter_nickname, content, timestamp, message_id, channel_id
            FROM quotes
            WHERE tick = 0
        """).fetchall()

        if not rows:
            cursor.execute("UPDATE quotes SET tick = 0 WHERE tick = 1")
            conn.commit()
            reset_quotes = True

            rows = cursor.execute("""
                SELECT rowid, author, author_nickname, quoter, quoter_nickname, content, timestamp, message_id, channel_id
                FROM quotes
                WHERE tick = 0
            """).fetchall()

        if rows:
            selected_quote = random.choice(rows)
            
            selected_rowid = selected_quote[0]
            

            quote_details = {
                "author": selected_quote[1],
                "author_nickname": selected_quote[2],
                "quoter": selected_quote[3],
                "quoter_nickname": selected_quote[4],
                "content": selected_quote[5],
                "timestamp": selected_quote[6],
                "message_id": selected_quote[7],
                "channel_id": selected_quote[8]
            }

        else:
            quote_details = None  # In case no quotes exist with tick = 0


        
        # Ensure we have a quote to display
        if not quote_details:
            await inter.response.send_message("No quotes available.")
            return

        # Resolve users if available, otherwise fall back to stored nicknames
        author_raw = quote_details.get("author")
        if isinstance(author_raw, (int, str)):
            try:
                author_id = int(author_raw)
            except (TypeError, ValueError):
                author_id = None
        else:
            author_id = None

        quoter_raw = quote_details.get("quoter")
        if isinstance(quoter_raw, (int, str)):
            try:
                quoter_id = int(quoter_raw)
            except (TypeError, ValueError):
                quoter_id = None
        else:
            quoter_id = None

        author = self.bot.get_user(author_id) if author_id else None
        quoted_by = self.bot.get_user(quoter_id) if quoter_id else None

        author_name = getattr(author, "display_name", None) or quote_details.get("author_nickname", "Unknown")
        quoted_by_name = getattr(quoted_by, "display_name", None) or quote_details.get("quoter_nickname", "Unknown")

        # timestamp may already be an int, handle both cases
        ts = int(quote_details.get("timestamp"))

        # Try to fetch the original message link
        channel_id = int(quote_details.get('channel_id'))
        print(f"Looking for channel with ID: {channel_id}")
        
        # Check if the channel exists in the guild
        channel = inter.guild.get_channel_or_thread(channel_id)
        if channel:
            try:
                original_message = await channel.fetch_message(int(quote_details.get('message_id')))
                link = original_message.jump_url
            except (disnake.NotFound, disnake.Forbidden):
                original_message = None
                link = "[message deleted or inaccessible]"
        else:
            original_message = None
            link = "[channel not found]"


        # Format the quote content
        content = quote_details.get("content", "")
        print(content)
        if not content or content == "":
            # If the content is empty, check if the original message has any attachments
            if original_message and original_message.attachments:
                prefixed = "\n".join(f"> ## {attachment.url}" for attachment in original_message.attachments)
            else:
                message = f"It seems like the message has no content *or* attachments...\n🔎 It was sent on <t:{ts}:F> by {author_name}\nif you **filter search** for messages sent on that day you can maybe **find the quote and re-quote it** to fix the issue\n\nFlagging quote {selected_rowid} as broken so that it doesn't show up again"
                cursor.execute("UPDATE quotes SET tick = 5 WHERE rowid = ?", (selected_rowid,))
                conn.commit()
                conn.close()

                await inter.response.send_message(content=message)
                return
        else:
            lines = content.splitlines()

            prefixed_lines = []
            for line in lines:
                #if an empty line is encountered, make it a new line with \n
                if line.strip() == "":
                    prefixed_lines.append("> ")
                    continue
                prefixed_line = f"> ## {line}"
                prefixed_lines.append(prefixed_line)

            prefixed = "\n".join(prefixed_lines)
            # prefixed = "\n".join(f"> ## {line}" for line in content.splitlines())

        # Construct the message
        message = (
            f'{prefixed[:1500]}\n'
            f'-# Sent on <t:{ts}:F> - {link}\n'
            f'-# **quoter:** {quoted_by_name} **| sender:** {author_name} | {selected_rowid}'
        )

        if reset_quotes:
            message += f'\n-# 🔄'

        await inter.response.send_message(content=message[:2000], allowed_mentions=disnake.AllowedMentions.none())

        cursor.execute("UPDATE quotes SET tick = 1 WHERE rowid = ?", (selected_rowid,))
        conn.commit()
        conn.close()


def setup(bot):
    bot.add_cog(Quotes(bot))
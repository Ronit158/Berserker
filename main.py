import os
import discord  
import random
from datetime import datetime

# ...existing code...
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

papa_replies = [
    "Papa is busy fixing the universe , wait for him to finish!",
    "Papa is busy Doing stuff, he'll get back to you soon! ",
    "Papa will reply soon, have patience ",
]
LOG_CHANNEL_ID = 1447991240435175637
# ...existing code...

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}!')

    async def on_message_delete(self, message):
        # Ignore bot messages
        if message.author.bot:
            return

        log_channel = self.get_channel(LOG_CHANNEL_ID)
        if not log_channel:
            return

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        author = f"{message.author} ({message.author.id})"
        content = message.content if message.content else "(No text content)"

        if message.attachments:
            content += "\nAttachments:\n" + "\n".join([a.url for a in message.attachments])

        embed = discord.Embed(
            title="Message Deleted",
            description=content,
            color=discord.Color.red(),
        )
        embed.set_author(
            name=str(message.author),
            icon_url=message.author.avatar.url if message.author.avatar else None
        )
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(
            name="Time",
            value=f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            inline=True
        )
        await log_channel.send(embed=embed)

    async def on_message(self, message):
        # Ignore bot messages (including self)
        if message.author.bot:
            return

        # Replies when specific user/role is mentioned
        if message.mentions:
            for user in message.mentions:
                if user.id == 592920980687683584:
                    await message.channel.send(random.choice(papa_replies))
                    break

        if message.role_mentions:
            for role in message.role_mentions:
                if role.id == 1375406481050173451:
                    await message.channel.send(random.choice(papa_replies))
                    break

        # Commands
        content = message.content or ""

        if content.lower() == "+resetnicks":
            if message.author.guild_permissions.administrator:
                await message.channel.send("⏳ Removing everyone's nicknames...")
                for member in message.guild.members:
                    try:
                        await member.edit(nick=None)
                    except:
                        pass
                await message.channel.send("All nicknames have been reset!")
            else:
                await message.channel.send("You need **Admin** permissions to use this command.")

        if content.startswith("+nick"):
            if not message.author.guild_permissions.administrator:
                await message.channel.send("Only **admins** can use this command.")
                return

            parts = content.split(" ", 2)
            if len(parts) < 3 or not message.mentions:
                await message.channel.send("Usage: `+nick @user newnickname`")
                return

            target_user = message.mentions[0]
            new_nick = parts[2]

            try:
                await target_user.edit(nick=new_nick)
                await message.channel.send(f"Nickname changed for {target_user.mention} to **{new_nick}**!")
            except:
                await message.channel.send("I don't have permission to change that user's nickname.")

        if content.startswith("+unnick"):
            if not message.author.guild_permissions.administrator:
                await message.channel.send("❌ Only **admins** can use this command.")
                return

            if not message.mentions:
                await message.channel.send("❌ Usage: `+unnick @user`")
                return

            target_user = message.mentions[0]

            try:
                await target_user.edit(nick=None)
                await message.channel.send(f"Nickname cleared for {target_user.mention}!")
            except:
                await message.channel.send("I don't have permission to remove that user's nickname.")

        if content.startswith("+help"):
            help_message = (
                "Here are the commands you can use:\n"
                "`+nick @user newnickname` - Change a user's nickname (Admin only)\n"
                "`+unnick @user` - Remove a user's nickname (Admin only)\n"
                "`+resetnicks` - Reset all nicknames in the server (Admin only)\n"
                "`+purge <number_of_messages>` - Delete a number of recent messages (Admin only)\n"
            )
            await message.channel.send(help_message)

        if content.startswith("+purge"):
            if not message.author.guild_permissions.administrator:
                await message.channel.send("Only admins can use this command.")
                return

            parts = content.split(" ")
            if len(parts) != 2 or not parts[1].isdigit():
                await message.channel.send("Usage: +purge <number_of_messages>")
                return

            count = int(parts[1])
            deleted = await message.channel.purge(limit=count + 1)
            await message.channel.send(f"Deleted {len(deleted)-1} messages!", delete_after=5)




client = Client(intents=intents)
client.run(os.environ['DISCORD_TOKEN'])



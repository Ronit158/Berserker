import os
import discord
import random
import asyncio
import requests
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
import json

app = Flask('')

#AI chat router
@app.route('/')
def home():
    return "Bot is running!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


# WORKING AI using currently active free APIs
def get_ai_response(user_message):
    """
    Uses TESTED working FREE AI APIs (December 2024)
    """

    # Add custom personality/identity responses
    user_message_lower = user_message.lower()

    # Identity questions
    if any(phrase in user_message_lower for phrase in
           ["who are you", "what are you", "your name", "who r u"]):
        return "I'm **Berserker's Bot**, a helpful AI assistant created to serve this Discord server!"

    if any(phrase in user_message_lower for phrase in
           ["who made you", "who created you", "your creator", "your owner"]):
        return "I was created by **Berserker** to help manage and assist in this server! "

    if any(phrase in user_message_lower for phrase in [
            "what can you do", "your features", "your abilities", "help me",
            "whats your job"
    ]):
        return "I can chat with you using AI, help with moderation, manage giveaways, track AFK status, and much more! Use `+help` to see all my commands."

    # Method 1: Pollinations AI (Very Reliable - No signup)
    try:
        response = requests.post("https://text.pollinations.ai/",
                                 json={
                                     "messages": [{
                                         "role": "user",
                                         "content": user_message
                                     }],
                                     "model":
                                     "openai"
                                 },
                                 headers={"Content-Type": "application/json"},
                                 timeout=30)

        if response.status_code == 200:
            result = response.text.strip()
            if result and len(result) > 0:
                return result
    except Exception as e:
        print(f"Method 1 failed: {e}")

    # Method 2: Pollinations AI Simple Endpoint
    try:
        response = requests.get(
            f"https://text.pollinations.ai/{requests.utils.quote(user_message)}",
            timeout=25)

        if response.status_code == 200:
            result = response.text.strip()
            if result and len(result) > 0:
                return result
    except Exception as e:
        print(f"Method 2 failed: {e}")

    # Method 3: AI ChatBot API
    try:
        response = requests.get(
            f"https://api.kvachq.top/gpt?text={requests.utils.quote(user_message)}",
            timeout=25)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'response' in data:
                return data['response'].strip()
    except Exception as e:
        print(f"Method 3 failed: {e}")

    # Method 4: TextSynth API (GPT-J)
    try:
        response = requests.post(
            "https://api.textsynth.com/v1/engines/gptj_6B/completions",
            json={
                "prompt": f"User: {user_message}\nAssistant:",
                "max_tokens": 200,
                "temperature": 0.7
            },
            headers={"Content-Type": "application/json"},
            timeout=30)

        if response.status_code == 200:
            data = response.json()
            if 'text' in data:
                result = data['text'].strip()
                if result:
                    return result
    except Exception as e:
        print(f"Method 4 failed: {e}")

    # Method 5: Kobold AI API
    try:
        response = requests.post(
            "https://api.koboldai.net/api/v1/generate",
            json={
                "prompt": f"### Instruction: {user_message}\n### Response:",
                "max_length": 200,
                "temperature": 0.7
            },
            headers={"Content-Type": "application/json"},
            timeout=30)

        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0].get('text', '').strip()
                if result:
                    return result
    except Exception as e:
        print(f"Method 5 failed: {e}")

    # Method 6: Simple AI Chat API
    try:
        response = requests.post("https://api.aiforthai.in.th/gpt-j6b",
                                 json={
                                     "text": user_message,
                                     "max_length": 200
                                 },
                                 headers={"Content-Type": "application/json"},
                                 timeout=25)

        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                return data['response'].strip()
    except Exception as e:
        print(f"Method 6 failed: {e}")

    return "❌ All AI services are temporarily unavailable. Please try again in a moment!"


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
WELCOME_CHANNEL_ID = 1375394399042801674  # Set your welcome channel ID here
# ...existing code...

# Storage for giveaways and AFK users
active_giveaways = {}
afk_users = {}

# Cooldown tracking for AI command
ai_cooldowns = {}
AI_COOLDOWN_SECONDS = 3


class Client(discord.Client):

    async def on_ready(self):
        print(f'Logged in as {self.user}!')
        print('✅ Bot is ready with AI chat (6 backup APIs)!')

    async def on_member_join(self, member):
        if WELCOME_CHANNEL_ID:
            channel = self.get_channel(WELCOME_CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title="Welcome!",
                    description=f"Welcome to the server, {member.mention}! 🎉",
                    color=discord.Color.green())
                embed.set_thumbnail(
                    url=member.avatar.url if member.avatar else None)
                embed.add_field(name="Member Count",
                                value=f"{member.guild.member_count}",
                                inline=True)
                await channel.send(embed=embed)

    async def on_member_remove(self, member):
        if WELCOME_CHANNEL_ID:
            channel = self.get_channel(WELCOME_CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title="Goodbye!",
                    description=f"{member.name} has left the server. 👋",
                    color=discord.Color.orange())
                embed.set_thumbnail(
                    url=member.avatar.url if member.avatar else None)
                await channel.send(embed=embed)

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
            content += "\nAttachments:\n" + "\n".join(
                [a.url for a in message.attachments])

        embed = discord.Embed(
            title="Message Deleted",
            description=content,
            color=discord.Color.red(),
        )
        embed.set_author(name=str(message.author),
                         icon_url=message.author.avatar.url
                         if message.author.avatar else None)
        embed.add_field(name="Channel",
                        value=message.channel.mention,
                        inline=True)
        embed.add_field(
            name="Time",
            value=f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            inline=True)
        await log_channel.send(embed=embed)

    async def on_message(self, message):
        # Ignore bot messages (including self)
        if message.author.bot:
            return

        # Check if user is back from AFK
        if message.author.id in afk_users:
            afk_data = afk_users.pop(message.author.id)

            # Calculate AFK duration
            afk_duration = datetime.utcnow() - afk_data['time']
            hours, remainder = divmod(int(afk_duration.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)

            # Format duration string
            duration_parts = []
            if hours > 0:
                duration_parts.append(f"{hours}h")
            if minutes > 0:
                duration_parts.append(f"{minutes}m")
            if seconds > 0 or not duration_parts:
                duration_parts.append(f"{seconds}s")
            duration_str = " ".join(duration_parts)

            # Restore original nickname
            try:
                await message.author.edit(nick=afk_data['original_nick'])
            except:
                pass  # If bot can't change nickname, continue anyway

            await message.channel.send(
                f"Welcome back {message.author.mention}! You were AFK for **{duration_str}** - {afk_data['reason']}"
            )

        # Check if mentioning AFK users
        for user in message.mentions:
            if user.id in afk_users:
                afk_data = afk_users[user.id]

                # Calculate AFK duration
                afk_duration = datetime.utcnow() - afk_data["time"]
                hours, remainder = divmod(int(afk_duration.total_seconds()),
                                          3600)
                minutes, seconds = divmod(remainder, 60)

                # Format clean duration
                duration_parts = []
                if hours > 0:
                    duration_parts.append(f"{hours}h")
                if minutes > 0:
                    duration_parts.append(f"{minutes}m")
                if seconds > 0 or not duration_parts:
                    duration_parts.append(f"{seconds}s")

                duration_str = " ".join(duration_parts)

                await message.channel.send(
                    f"{user.name} is currently AFK — **{duration_str}**\nReason: *{afk_data['reason']}*"
                )

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

        # Get message content
        content = message.content or ""

        # Handle bot mentions - check if bot is mentioned
        if self.user.mentioned_in(message):
            # Remove the bot mention from the content
            content_without_mention = content.replace(
                f'<@{self.user.id}>', '').replace(f'<@!{self.user.id}>',
                                                  '').strip()

            # If there's a command after the mention, process it as if it had + prefix
            if content_without_mention:
                # Add + prefix if not already there
                if not content_without_mention.startswith('+'):
                    content = '+' + content_without_mention
                else:
                    content = content_without_mention
            else:
                # Just the bot mention with nothing else - show help prompt
                await message.channel.send(
                    "👋 Hello! Please use `+help` to see all available commands."
                )
                return

        # AI Chat Command - 6 BACKUP APIS!
        if content.startswith("+ai"):
            # Check cooldown
            user_id = message.author.id
            current_time = datetime.utcnow()

            if user_id in ai_cooldowns:
                time_diff = (current_time -
                             ai_cooldowns[user_id]).total_seconds()
                if time_diff < AI_COOLDOWN_SECONDS:
                    remaining = int(AI_COOLDOWN_SECONDS - time_diff)
                    await message.channel.send(
                        f"⏳ Please wait {remaining}s before using +ai again.")
                    return

            # Get user message
            parts = content.split(" ", 1)
            if len(parts) < 2:
                await message.channel.send(
                    "Usage: `+ai <your message>`\n"
                    "Example: `+ai Explain black holes simply`")
                return

            user_message = parts[1]

            # Show typing indicator
            async with message.channel.typing():
                # Update cooldown
                ai_cooldowns[user_id] = current_time

                # Get AI response (run in executor to not block)
                loop = asyncio.get_event_loop()
                ai_response = await loop.run_in_executor(
                    None, get_ai_response, user_message)

                # Send response
                if len(ai_response) > 1900:
                    chunks = [
                        ai_response[i:i + 1900]
                        for i in range(0, len(ai_response), 1900)
                    ]
                    for chunk in chunks:
                        await message.channel.send(f"🤖 {chunk}")
                else:
                    await message.channel.send(f"🤖 {ai_response}")

        # AFK System
        if content.startswith("+afk"):
            parts = content.split(" ", 1)
            reason = parts[1] if len(parts) > 1 else "AFK"

            # Store original nickname
            original_nick = message.author.display_name
            afk_users[message.author.id] = {
                "reason": reason,
                "time": datetime.utcnow(),
                "original_nick": original_nick
            }

            # Change nickname to [AFK] prefix
            try:
                new_nick = f"[AFK]{original_nick}"
                # Discord nicknames have a 32 character limit
                if len(new_nick) > 32:
                    new_nick = new_nick[:32]
                await message.author.edit(nick=new_nick)
            except:
                pass  # If bot can't change nickname, continue anyway

            await message.channel.send(
                f"{message.author.mention} is now AFK: {reason}")

        # Ban System
        if content.startswith("+ban"):
            if not message.author.guild_permissions.ban_members:
                await message.channel.send(
                    "You need **Ban Members** permission to use this command.")
                return

            if not message.mentions:
                await message.channel.send("Usage: `+ban @user [reason]`")
                return

            target = message.mentions[0]
            parts = content.split(" ", 2)
            reason = parts[2] if len(parts) > 2 else "No reason provided"

            try:
                await target.ban(reason=reason)
                embed = discord.Embed(
                    title="User Banned",
                    description=f"{target.mention} has been banned.",
                    color=discord.Color.red())
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator",
                                value=message.author.mention,
                                inline=True)
                await message.channel.send(embed=embed)
            except:
                await message.channel.send(
                    "I don't have permission to ban that user.")

        # Kick System
        if content.startswith("+kick"):
            if not message.author.guild_permissions.kick_members:
                await message.channel.send(
                    "You need **Kick Members** permission to use this command."
                )
                return

            if not message.mentions:
                await message.channel.send("Usage: `+kick @user [reason]`")
                return

            target = message.mentions[0]
            parts = content.split(" ", 2)
            reason = parts[2] if len(parts) > 2 else "No reason provided"

            try:
                await target.kick(reason=reason)
                embed = discord.Embed(
                    title="User Kicked",
                    description=f"{target.mention} has been kicked.",
                    color=discord.Color.orange())
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator",
                                value=message.author.mention,
                                inline=True)
                await message.channel.send(embed=embed)
            except:
                await message.channel.send(
                    "I don't have permission to kick that user.")

        if content.startswith("+message"):
            # Only allow admins to use it
            if not message.author.guild_permissions.administrator:
                await message.channel.send("Only admins can use this command.")
                return

            parts = content.split(" ", 2)
            if len(parts) < 3:
                await message.channel.send(
                    "Usage: `+message #channel_name Your message here`")
                return

            # Extract channel and message
            channel_mention = parts[1]
            msg_to_send = parts[2]

            # Get channel object
            if channel_mention.startswith("<#") and channel_mention.endswith(
                    ">"):
                channel_id = int(channel_mention[2:-1])
                target_channel = message.guild.get_channel(channel_id)
            else:
                # fallback: try to get by name
                target_channel = discord.utils.get(
                    message.guild.channels, name=channel_mention.strip("#"))

            if not target_channel:
                await message.channel.send("❌ Could not find that channel.")
                return

            # Send the message
            await target_channel.send(msg_to_send)
            await message.channel.send(
                f"✅ Message sent to {target_channel.mention}!")

        # Giveaway System
        #if content.startswith("poll"):
        if content.startswith("+gstart"):
            if not message.author.guild_permissions.administrator:
                await message.channel.send(
                    "Only **admins** can start giveaways.")
                return

            parts = content.split(" ", 3)
            if len(parts) < 4:
                await message.channel.send(
                    "Usage: `+gstart <time_in_seconds> <winners> <prize>`")
                return

            try:
                duration = int(parts[1])
                winners = int(parts[2])
                prize = parts[3]
            except ValueError:
                await message.channel.send("Time and winners must be numbers!")
                return

            giveaway_embed = discord.Embed(
                title="🎉 GIVEAWAY 🎉",
                description=
                f"**Prize:** {prize}\n**Winners:** {winners}\n**Ends in:** {duration} seconds\n\nReact with 🎉 to enter!",
                color=discord.Color.blue())
            giveaway_embed.set_footer(text=f"Hosted by {message.author.name}")

            giveaway_msg = await message.channel.send(embed=giveaway_embed)
            await giveaway_msg.add_reaction("🎉")

            active_giveaways[giveaway_msg.id] = {
                "channel_id": message.channel.id,
                "prize": prize,
                "winners": winners,
                "end_time": datetime.utcnow() + timedelta(seconds=duration),
                "host": message.author.id
            }

            await asyncio.sleep(duration)

            # Get participants
            giveaway_msg = await message.channel.fetch_message(giveaway_msg.id)
            reaction = discord.utils.get(giveaway_msg.reactions, emoji="🎉")
            if reaction:
                users = [
                    user async for user in reaction.users() if not user.bot
                ]
                if len(users) >= winners:
                    winners_list = random.sample(users, winners)
                    winner_mentions = ", ".join(
                        [w.mention for w in winners_list])
                    await message.channel.send(
                        f"🎉 Congratulations {winner_mentions}! You won **{prize}**!"
                    )
                else:
                    await message.channel.send(
                        f"Not enough participants for the giveaway!")

            if giveaway_msg.id in active_giveaways:
                del active_giveaways[giveaway_msg.id]

        if content.startswith("+resetnicks"):
            if message.author.guild_permissions.administrator:
                await message.channel.send("⏳ Removing everyone's nicknames..."
                                           )
                for member in message.guild.members:
                    try:
                        await member.edit(nick=None)
                    except:
                        pass
                await message.channel.send("All nicknames have been reset!")
            else:
                await message.channel.send(
                    "You need **Admin** permissions to use this command.")

        if content.startswith("+nick"):
            if not message.author.guild_permissions.administrator:
                await message.channel.send(
                    "Only **admins** can use this command.")
                return

            parts = content.split(" ", 2)
            if len(parts) < 3 or not message.mentions:
                await message.channel.send("Usage: `+nick @user newnickname`")
                return

            target_user = message.mentions[0]
            new_nick = parts[2]

            try:
                await target_user.edit(nick=new_nick)
                await message.channel.send(
                    f"Nickname changed for {target_user.mention} to **{new_nick}**!"
                )
            except:
                await message.channel.send(
                    "I don't have permission to change that user's nickname.")

        if content.startswith("+unnick"):
            if not message.author.guild_permissions.administrator:
                await message.channel.send(
                    "Only **admins** can use this command.")
                return

            if not message.mentions:
                await message.channel.send("Usage: `+unnick @user`")
                return

            target_user = message.mentions[0]

            try:
                await target_user.edit(nick=None)
                await message.channel.send(
                    f"Nickname cleared for {target_user.mention}!")
            except:
                await message.channel.send(
                    "I don't have permission to remove that user's nickname.")

        if content.startswith("+help"):
            help_message = (
                "**📋 Available Commands:**\n\n"
                "**AI Chat:**\n"
                "`+ai <message>` - Chat with real AI\n"
                "Example: `+ai Hello`\n\n"
                "**Moderation:**\n"
                "`+ban @user [reason]` - Ban a user (Ban Members permission)\n"
                "`+kick @user [reason]` - Kick a user (Kick Members permission)\n"
                "`+purge <number>` - Delete messages (Admin only)\n\n"
                "**Nickname Management:**\n"
                "`+nick @user newnickname` - Change a user's nickname (Admin only)\n"
                "`+unnick @user` - Remove a user's nickname (Admin only)\n"
                "`+resetnicks` - Reset all nicknames (Admin only)\n\n"
                "**Giveaways:**\n"
                "`+gstart <seconds> <winners> <prize>` - Start a giveaway (Admin only)\n\n"
                "**Utility:**\n"
                "`+afk [reason]` - Set yourself as AFK\n\n"
                "**💡 Tip:** You can also mention me with a command! Example: `@BerserkersBot help`"
            )
            await message.channel.send(help_message)

        if content.startswith("+purge"):
            if not message.author.guild_permissions.administrator:
                await message.channel.send("Only admins can use this command.")
                return

            parts = content.split(" ")
            if len(parts) != 2 or not parts[1].isdigit():
                await message.channel.send("Usage: +purge <number_of_messages>"
                                           )
                return

            count = int(parts[1])
            deleted = await message.channel.purge(limit=count + 1)
            await message.channel.send(f"Deleted {len(deleted)-1} messages!",
                                       delete_after=5)


keep_alive()
client = Client(intents=intents)
client.run(os.environ['DISCORD_TOKEN'])



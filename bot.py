import discord
import re
import os

# Grab token from environment variable (set this in Railway/your host)
TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Matches custom emoji like <:name:123456> or animated <a:name:123456>
CUSTOM_EMOJI_RE = re.compile(r"<(a?):(\w+):(\d+)>")

# Matches a single Unicode emoji (covers most standard emoji)
UNICODE_EMOJI_RE = re.compile(
    "[\U0001F300-\U0001F9FF"
    "\U00002600-\U000027BF"
    "\U0001FA00-\U0001FA9F"
    "\U0001F004\U0001F0CF"
    "\U000024C2-\U0001F251]+",
    re.UNICODE,
)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Only handle messages starting with --jumbo
    if not message.content.startswith("--jumbo "):
        return

    # Extract everything after "--jumbo "
    argument = message.content[len("--jumbo "):].strip()

    image_url = None
    emoji_name = None

    # Check for custom Discord emoji first
    custom_match = CUSTOM_EMOJI_RE.search(argument)
    if custom_match:
        animated, name, emoji_id = custom_match.groups()
        ext = "gif" if animated else "png"
        image_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}?size=256"
        emoji_name = name

    # Fall back to Unicode emoji
    if not image_url:
        unicode_match = UNICODE_EMOJI_RE.search(argument)
        if unicode_match:
            emoji_char = unicode_match.group(0)
            # Convert emoji to its hex codepoint(s) for the CDN URL
            codepoints = "-".join(f"{ord(c):x}" for c in emoji_char)
            image_url = f"https://emojicdn.elk.sh/{emoji_char}?style=twitter"
            emoji_name = codepoints

    if not image_url:
        await message.reply("❌ Couldn't find a valid emoji in that message.")
        return

    # Build the embed
    embed = discord.Embed(color=0x5865F2)  # Discord blurple
    embed.set_image(url=image_url)
    embed.set_footer(text=f":{emoji_name}:")

    await message.reply(embed=embed, mention_author=False)

client.run(TOKEN)

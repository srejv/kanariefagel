import discord
import re
import os

TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

CUSTOM_EMOJI_RE = re.compile(r"<(a?):(\w+):(\d+)>")
UNICODE_EMOJI_RE = re.compile(
    "[\U0001F300-\U0001F9FF"
    "\U00002600-\U000027BF"
    "\U0001FA00-\U0001FA9F"
    "\U0001F004\U0001F0CF"
    "\U000024C2-\U0001F251]+",
    re.UNICODE,
)

def parse_emojis(text):
    """Return a list of (image_url, name) tuples for all emoji found in text."""
    results = []
    # We'll scan through the string, picking off custom and unicode emoji in order
    i = 0
    while i < len(text):
        # Try custom emoji at current position
        custom_match = CUSTOM_EMOJI_RE.match(text, i)
        if custom_match:
            animated, name, emoji_id = custom_match.groups()
            ext = "gif" if animated else "png"
            url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}?size=256"
            results.append((url, name))
            i = custom_match.end()
            continue

        # Try unicode emoji at current position
        unicode_match = UNICODE_EMOJI_RE.match(text, i)
        if unicode_match:
            emoji_char = unicode_match.group(0)
            url = f"https://emojicdn.elk.sh/{emoji_char}?style=twitter"
            name = "-".join(f"{ord(c):x}" for c in emoji_char)
            results.append((url, name))
            i = unicode_match.end()
            continue

        i += 1

    return results

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith("--jumbo "):
        return

    argument = message.content[len("--jumbo "):].strip()
    emojis = parse_emojis(argument)

    if not emojis:
        await message.reply("❌ Couldn't find any valid emoji in that message.")
        return

    # Build one embed per emoji (Discord embeds only support one large image each)
    embeds = []
    for url, name in emojis[:10]:  # cap at 10 to avoid spam
        embed = discord.Embed(color=0x5865F2)
        embed.set_image(url=url)
        # embed.set_footer(text=f":{name}:")
        embeds.append(embed)

    await message.reply(embeds=embeds, mention_author=False)

client.run(TOKEN)
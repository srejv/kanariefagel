import discord
import re
import os
import io
import httpx
from PIL import Image

TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

CUSTOM_EMOJI_RE = re.compile(r"<(a?):(\w+):(\d+)>")
UNICODE_EMOJI_RE = re.compile(
    "[\U0001F300-\U0001F9FF"
    "\U00002600-\U000027BF"
    "\U0001FA00-\U0001FA9F"
    "\U0001F004"
    "\U0001F0CF]",
    re.UNICODE,
)

EMOJI_SIZE = 128
PADDING = 16


def unicode_to_twemoji_url(emoji_char: str) -> str:
    codepoints = "-".join(
        f"{ord(c):x}" for c in emoji_char if ord(c) != 0xFE0F
    )
    return f"https://cdn.jsdelivr.net/gh/jdecked/twemoji@latest/assets/72x72/{codepoints}.png"


def parse_emojis(text):
    results = []
    i = 0
    while i < len(text):
        custom_match = CUSTOM_EMOJI_RE.match(text, i)
        if custom_match:
            animated, name, emoji_id = custom_match.groups()
            url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png?size=256"
            results.append((url, name))
            i = custom_match.end()
            continue

        unicode_match = UNICODE_EMOJI_RE.match(text, i)
        if unicode_match:
            emoji_char = unicode_match.group(0)
            url = unicode_to_twemoji_url(emoji_char)
            results.append((url, emoji_char))
            i = unicode_match.end()
            continue

        i += 1
    return results


async def fetch_image(url: str) -> Image.Image | None:
    try:
        async with httpx.AsyncClient(timeout=10) as http:
            r = await http.get(url, follow_redirects=True)
            r.raise_for_status()
            img = Image.open(io.BytesIO(r.content)).convert("RGBA")
            img = img.resize((EMOJI_SIZE, EMOJI_SIZE), Image.LANCZOS)
            return img
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None


async def build_composite(images: list[Image.Image]) -> io.BytesIO:
    n = len(images)
    width = n * EMOJI_SIZE + (n - 1) * PADDING
    canvas = Image.new("RGBA", (width, EMOJI_SIZE), (0, 0, 0, 0))
    for i, img in enumerate(images):
        canvas.paste(img, (i * (EMOJI_SIZE + PADDING), 0), img)
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    buf.seek(0)
    return buf


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith("-jumbo "):
        return

    argument = message.content[len("-jumbo "):].strip()
    emojis = parse_emojis(argument)[:10]

    if not emojis:
        await message.channel.send("❌ Couldn't find any valid emoji in that message.")
        return

    if len(emojis) == 1:
        url, name = emojis[0]
        embed = discord.Embed(color=0x5865F2)
        embed.set_image(url=url)
        # embed.set_footer(text=f":{name}:")
        await message.channel.send(embed=embed)
        return

    async with message.channel.typing():
        images = []
        for url, _ in emojis:
            img = await fetch_image(url)
            if img:
                images.append(img)

        if not images:
            await message.channel.send("❌ Couldn't fetch any of those emoji.")
            return

        buf = await build_composite(images)
        await message.channel.send(
            file=discord.File(buf, filename="jumbo.png"),
            mention_author=False,
        )

client.run(TOKEN)
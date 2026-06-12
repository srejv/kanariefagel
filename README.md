# Jumbo Emoji Bot

Replies to `--jumbo <emoji>` with a large embed version of that emoji.

## Supports
- Custom server emoji: `--jumbo :pepe:`
- Animated emoji: `--jumbo :pepedance:`
- Standard Unicode emoji: `--jumbo 🔥`

## Local setup

```bash
pip install -r requirements.txt
export DISCORD_TOKEN="your-token-here"
python bot.py
```

## Deploy to Railway (recommended)

1. Push this folder to a GitHub repo
2. Go to https://railway.app → New Project → Deploy from GitHub
3. Add an environment variable: `DISCORD_TOKEN` = your bot token
4. Railway auto-detects Python and runs `python bot.py`

## Discord bot setup

1. https://discord.com/developers/applications → New Application
2. Bot tab → Add Bot → copy the token
3. Bot tab → enable "Message Content Intent"
4. OAuth2 → URL Generator → check `bot` + permissions:
   - Read Messages
   - Send Messages
   - Embed Links
5. Use the generated URL to invite the bot to your server

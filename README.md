# Paperclip Telegram Userbot

Pyrogram-based userbot for Paperclip agents to send/receive Telegram messages.
Useful for E2E testing of Telegram bots.

## API

- `POST /send` — send a message to a peer (bot username, chat id, or phone).
- `GET /history/{peer}` — get recent messages from a peer.
- `POST /wait` — wait for a message from a peer within a timeout.
- `GET /health` — health check.

## First run / auth

The userbot needs to authorize once with Telegram:

```bash
docker compose run --rm userbot python -m paperclip_userbot.auth
```

It will prompt for the phone code sent to +799...240.

After authorization, `paperclip_userbot.session` is created. Keep it in the bind-mounted `data/` directory.

## Running

```bash
docker compose up -d
```

## E2E example

```bash
curl -X POST http://127.0.0.1:8700/send \
  -H "Content-Type: application/json" \
  -d '{"peer":"@Cyberkitty1319_bot","text":"hello"}'

curl "http://127.0.0.1:8700/history/@Cyberkitty1319_bot?limit=5"
```

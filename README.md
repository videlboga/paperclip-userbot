# Paperclip Telegram Userbot

Pyrogram-based userbot for Paperclip agents to send/receive Telegram messages.
Useful for E2E testing of Telegram bots.

## API

- `POST /send` — send a message to a peer (bot username, chat id, or phone).
- `GET /history/{peer}` — get recent messages from a peer.
- `POST /wait` — wait for a message from a peer within a timeout.
- `GET /health` — health check.

## First run / auth

The userbot needs to authorize once with Telegram. Interactive mode will prompt for
`api_id`, `api_hash`, phone number and confirmation code:

```bash
docker compose run --rm -it userbot python -m paperclip_userbot.auth
```

You can also pass them via environment variables:

```bash
docker compose run --rm \
  -e API_ID=your_api_id \
  -e API_HASH=your_api_hash \
  -e PHONE_NUMBER=+799...240 \
  -e PHONE_CODE=12345 \
  userbot python -m paperclip_userbot.auth
```

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

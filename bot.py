import os
import re
import asyncio
import requests
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
SOURCE_CHANNEL = os.environ.get("SOURCE_CHANNEL")
AFFILIATE_TAG = os.environ.get("AFFILIATE_TAG")

LAST_ID_FILE = "last_id.txt"

def get_last_id():
    if os.path.exists(LAST_ID_FILE):
        with open(LAST_ID_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def save_last_id(msg_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(msg_id))

def convert_link(text):
    if not text:
        return text
    if "amazon.in" in text or "amzn.to" in text:
        if "tag=" in text:
            text = re.sub(r'tag=[a-zA-Z0-9-_]+', f'tag={AFFILIATE_TAG}', text)
        else:
            text = text + f"\n\n🔗 Shop via our link: tag={AFFILIATE_TAG}"
    return text

async def main():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    
    last_id = get_last_id()
    print(f"Last processed message ID: {last_id}")
    
    messages = await client.get_messages(SOURCE_CHANNEL, limit=5, min_id=last_id)
    
    if not messages:
        print("No new deals found.")
        return

    max_id = last_id
    for message in reversed(messages):
        if message.id > max_id:
            max_id = message.id
        
        if message.text:
            new_text = convert_link(message.text)
            bot_api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": CHANNEL_ID,
                "text": new_text,
                "parse_mode": "Markdown"
            }
            
            if not message.media:
                res = requests.post(bot_api_url, json=payload)
                if res.status_code == 200:
                    print(f"Posted message ID {message.id}")
                else:
                    print(f"Failed to post {message.id}: {res.text}")

    save_last_id(max_id)
    print(f"Updated last_id to {max_id}")

asyncio.run(main())

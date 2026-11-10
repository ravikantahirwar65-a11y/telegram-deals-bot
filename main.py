import os
import re
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import quote
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Health check web server for Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def start_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=start_server, daemon=True).start()

# Telegram Credentials
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

SOURCE_CHANNELS = [
    "lootdealsk_Alibaba_dc_DealDost"
]

TARGET_CHANNEL = "lootyahahai"
EARNKARO_USER_ID = "5777285"

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

def convert_to_earnkaro(url):
    encoded_url = quote(url, safe='')
    return f"https://earnkaro.com?r={EARNKARO_USER_ID}&url={encoded_url}"

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    message_text = event.message.message or ""
    urls = re.findall(r'(https?://[^\s]+)', message_text)
    
    if not urls and not event.message.media:
        return

    new_text = message_text
    for url in urls:
        affiliate_url = convert_to_earnkaro(url)
        new_text = new_text.replace(url, affiliate_url)
    
    footer = f"\n\n🔥 Join 👉 @{TARGET_CHANNEL} for Instant Deals"
    final_caption = new_text + footer

    try:
        if event.message.media:
            await client.send_file(TARGET_CHANNEL, event.message.media, caption=final_caption)
        else:
            await client.send_message(TARGET_CHANNEL, final_caption)
        print("✅ Deal posted successfully!")
    except Exception as e:
        print(f"❌ Send Error: {e}")

async def main():
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ SESSION_STRING Invalid! Login required.")
        return
    print("🚀 Telethon Userbot is authorized and actively monitoring channels!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

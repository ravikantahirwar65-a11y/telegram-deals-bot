import os
import re
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from urllib.parse import quote
from telethon import TelegramClient, events

# Environment variables se details uthayega
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

SOURCE_CHANNEL = "lootdealsk_Alibaba_dc_DealDost"
TARGET_CHANNEL = "lootyahahai"
EARNKARO_USER_ID = "5777285"

# Dummy web server Render ko Live dikhane ke liye
class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running Healthy!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

client = TelegramClient('deals_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def convert_to_earnkaro(url):
    encoded_url = quote(url, safe='')
    return f"https://earnkaro.com?r={EARNKARO_USER_ID}&url={encoded_url}"

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    message_text = event.message.message or ""
    
    # URL extract karna
    urls = re.findall(r'(https?://[^\s]+)', message_text)
    
    if not urls and not event.message.media:
        return

    # Links ko replace karna EarnKaro affiliate link se
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
        print("✅ Deal successfully converted and posted to channel!")
    except Exception as e:
        print(f"❌ Error: {e}")

print("🚀 Bot is running and monitoring deals...")
client.run_until_disconnected()

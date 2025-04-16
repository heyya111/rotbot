import os
import discord
import requests
import asyncio
from flask import Flask
from threading import Thread

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
MENTION_ID = os.getenv("MENTION_ID")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

client = discord.Client(intents=intents)

last_seen_ids = []

async def check_listings():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    print("📡 Channel fetched in listings:", channel.name if channel else "None")

    while not client.is_closed():
        try:
            url = "https://api-mainnet.magiceden.dev/v2/collections/cryptotitans/listings?offset=0&limit=20"
            response = requests.get(url)
            data = response.json()

            for listing in reversed(data):  # older first
                listing_id = listing.get("tokenMint")
                if listing_id in last_seen_ids:
                    continue

                last_seen_ids.append(listing_id)
                if len(last_seen_ids) > 50:
                    last_seen_ids.pop(0)

                price = listing.get("price")
                token = listing.get("tokenMint")
                link = f"https://magiceden.io/item-details/{token}"
                name = listing.get("token", {}).get("name", "Unknown Titan")
                image = listing.get("token", {}).get("image")

                attributes = listing.get("token", {}).get("attributes", [])
                traits = {attr["trait_type"]: attr["value"] for attr in attributes}
                trait_fields = [
                    "Element", "Elemental 1", "Elemental 2", "Elemental 3", "Elemental 4",
                    "Attack 5", "Attack 6", "Defense 7", "Defense 8", "Support 9"
                ]
                trait_text = "\n".join(
                    f"**{t}**: {traits.get(t, '—')}" for t in trait_fields
                )

                embed = discord.Embed(
                    title=f"{name} listed for {price} SOL",
                    url=link,
                    description=trait_text,
                    color=0x00ffcc
                )
                if image:
                    embed.set_image(url=image)

                await channel.send(content=f"<@{MENTION_ID}>", embed=embed)
                print(f"✅ New listing sent: {listing_id}")

        except Exception as e:
            print("Error while checking listings:", e)

        await asyncio.sleep(10)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        print("📡 Channel fetched on startup:", channel.name)

app = Flask(__name__)

@app.route('/')
def home():
    return "CryptoTitan bot is live."

def run_flask():
    app.run(host="0.0.0.0", port=3000)

Thread(target=run_flask).start()
client.loop.create_task(check_listings())
print("🟢 Starting Discord client...")
client.run(TOKEN)

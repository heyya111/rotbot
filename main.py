from flask import Flask
from threading import Thread
import discord
import requests
import asyncio
import time
import os

app = Flask('')

@app.route('/')
def home():
    return "✅ CryptoTitan bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1359805454733148311
MENTION_ID = 859114146523512843  # heyya11's ID
USER_ID = 859114146523512843     # user to DM

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # needed to fetch user by ID
client = discord.Client(intents=intents)

seen_ids = set()

target_traits = {
    "element", "elemental 1", "elemental 2", "elemental 3", "elemental 4",
    "attack 5", "attack 6", "defense 7", "defense 8", "support 9"
}

async def check_listings():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    user = await client.fetch_user(USER_ID)

    print(f"📡 Channel fetched in listings: {channel}")
    print(f"📨 User fetched for DM: {user}")

    if not channel or not user:
        print("❌ ERROR: Channel or user not found.")
        return

    while True:
        try:
            url = "https://api-mainnet.magiceden.dev/v2/collections/cryptotitans/listings?offset=0&limit=20"
            response = requests.get(url)
            data = response.json()

            for listing in data:
                listing_id = listing.get("tokenMint")
                price = listing.get("price")
                token_data = listing.get("token", {})
                name = token_data.get("name", "Unknown Titan")
                image_url = token_data.get("image", "")
                attributes = token_data.get("attributes", [])

                if listing_id not in seen_ids:
                    seen_ids.add(listing_id)

                    filtered_traits = [
                        f"**{attr['trait_type']}**: {attr['value']}"
                        for attr in attributes
                        if attr['trait_type'].lower() in target_traits
                    ]

                    traits_text = "\n".join(filtered_traits) or "No matching traits found"

                    embed = discord.Embed(
                        title=f"🛎️ {name} listed!",
                        description=f"**Price:** {price} SOL\n[🔗 View on Magic Eden](https://magiceden.io/item-details/{listing_id})",
                        color=0x00ffcc
                    )
                    embed.set_image(url=image_url)
                    embed.add_field(name="Traits", value=traits_text, inline=False)

                    await channel.send(f"<@{MENTION_ID}>")
                    await channel.send(embed=embed)
                    await user.send(embed=embed)

                    print(f"✅ Sent listing to channel + DMs: {listing_id}")

        except Exception as e:
            print(f"❌ Error: {e}")

        await asyncio.sleep(10)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    client.loop.create_task(check_listings())

keep_alive()

while True:
    try:
        client.run(TOKEN)
    except Exception as e:
        print(f"💥 Bot crashed: {e}")
        time.sleep(5)

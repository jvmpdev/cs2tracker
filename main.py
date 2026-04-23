import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv, set_key
import os
import requests

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
steam_api_key = os.getenv('STEAM_API_KEY')
steam_id = os.getenv('STEAM_ID')
steam_auth_code = os.getenv('STEAM_AUTH_CODE')
last_match_token = os.getenv('LAST_MATCH_TOKEN')
channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))

ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def update_last_token(new_token):
    global last_match_token
    last_match_token = new_token
    set_key(ENV_PATH, 'LAST_MATCH_TOKEN', new_token)

@bot.event
async def on_ready():
    print(f"initialised {bot.user.name}")
    check_new_match.start()

@tasks.loop(minutes=3)
async def check_new_match():
    try:
        response = requests.get(
            "https://api.steampowered.com/ICSGOPlayers_730/GetNextMatchSharingCode/v1",
            params={
                "key": steam_api_key,
                "steamid": steam_id,
                "steamidkey": steam_auth_code,
                "knowncode": last_match_token
            }
        )

        print(response.status_code)
        print(response.text)

        response2 = requests.get(
            "https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/",
            params={
                "key": steam_api_key,
                "steamid": steam_id,
                "appid": 730
            }
        )

        response3 = requests.get(
            "https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/",
            params={
                "key": steam_api_key,
                "steamid": steam_id,
                "appid": 730
            }
        )
        print(response3.text)
        print(response2.text)

        data = response.json()

        if "result" in data and data["result"].get("nextcode") != "n/a":
            new_token = data["result"]["nextcode"]
            update_last_token(new_token)
            print(f"New match found: {new_token}")
            await send_match_embed(new_token)
        else:
            print("No new match yet")

    except Exception as e:
        print(f"error checking match: {e}")

async def send_match_embed(match_token):
    channel = bot.get_channel(channel_id)
    embed = discord.Embed(
        title="Match Completed",
        color=discord.Color.green()
    )
    embed.add_field(name="Match Token", value=match_token, inline=False)
    embed.set_footer(text="CS2 Tracker")

    await channel.send(embed=embed)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
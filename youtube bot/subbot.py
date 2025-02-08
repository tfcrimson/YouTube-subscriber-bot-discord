import discord
import requests
import asyncio
import re
from discord.ext import commands
import json
import os
from googleapiclient.discovery import build

with open('config.json') as f:
    cfg = json.load(f)

DISCORD_BOT_TOKEN = cfg['bot_token']
BOT_PREFIX = "?" 
BOT_COLOR = int(cfg['color'], 16)
BOT_CHANNEL_1 = cfg['bot_channel1']
BOT_CHANNEL_2 = cfg['bot_channel2']
DONT_CHANGE = cfg['dont_change']
COOKIE_FILE = cfg['cookie_file'] 

YOUTUBE_ROLE_1 = cfg['role1']
YOUTUBE_ROLE_2 = cfg['role2']
YOUTUBE_ROLE_3 = cfg['role3']
YOUTUBE_ROLE_4 = cfg['role4']
YOUTUBE_ROLE_5 = cfg['role5']
DEFAULT_AMOUNT = cfg['default_amount']
YOUTUBE_ROLE1_AMOUNT = cfg['role1_amount']
YOUTUBE_ROLE2_AMOUNT = cfg['role2_amount']
YOUTUBE_ROLE3_AMOUNT = cfg['role3_amount']
YOUTUBE_ROLE4_AMOUNT = cfg['role4_amount']
YOUTUBE_ROLE5_AMOUNT = cfg['role5_amount']

def extract_channel_id(channel_link):
    """Extracts YouTube channel ID from a given link."""
    match = re.search(r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:channel\/|c\/|user\/)?([^\/\?\&]+)", channel_link)

    if match:
        return match.group(1)
    return None

def load_cookies(file_path):
    with open(file_path, "r") as f:
        cookies_str = f.read().strip()
    cookies = dict(map(lambda pair: pair.split("="), cookies_str.split("; ")))
    return cookies

def create_headers(cookies):
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
        "Cookie": "; ".join([f"{key}={value}" for key, value in cookies.items()])
    }

async def send_subscription(bot, channel_id, amount, headers):
    url = f"https://www.youtube.com/channel/{channel_id}/sub confirm"
    params = {
        "sub_confirmed_for_user": "1",
        "suggested_donation": "0",
        "confirmation_reason": "test"
    }
    for _ in range(amount):
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=BOT_PREFIX, help_command=None, intents=intents)

@bot.command(name="sub")
async def sub(ctx, channel_link: str):

    """Handles the ?sub command using a YouTube channel link."""
    if ctx.channel.id not in [int(BOT_CHANNEL_1), int(BOT_CHANNEL_2)]:
        return  

    if DONT_CHANGE:
        await ctx.send("Change config dont_change to false", delete_after=5)
        return

    channel_id = extract_channel_id(channel_link)
    if not channel_id:
        await ctx.send(f"Invalid YouTube link: **{channel_link}**", delete_after=5)
        return

    role1 = discord.utils.get(ctx.guild.roles, name=YOUTUBE_ROLE_1)
    role2 = discord.utils.get(ctx.guild.roles, name=YOUTUBE_ROLE_2)
    role3 = discord.utils.get(ctx.guild.roles, name=YOUTUBE_ROLE_3)
    role4 = discord.utils.get(ctx.guild.roles, name=YOUTUBE_ROLE_4)
    role5 = discord.utils.get(ctx.guild.roles, name=YOUTUBE_ROLE_5)

    sub_amount = DEFAULT_AMOUNT
    if role5 in ctx.author.roles:
        sub_amount = YOUTUBE_ROLE5_AMOUNT
    elif role4 in ctx.author.roles:
        sub_amount = YOUTUBE_ROLE4_AMOUNT
    elif role3 in ctx.author.roles:
        sub_amount = YOUTUBE_ROLE3_AMOUNT
    elif role2 in ctx.author.roles:
        sub_amount = YOUTUBE_ROLE2_AMOUNT
    elif role1 in ctx.author.roles:
        sub_amount = YOUTUBE_ROLE1_AMOUNT

    cookies = load_cookies(COOKIE_FILE)
    headers = create_headers(cookies)

    embed = discord.Embed(
        title="YouTube Subscribers",
        description=f"Sending **{sub_amount}** subscriptions to [this channel]({channel_link})",
        color=BOT_COLOR
    )
    await ctx.send(embed=embed, delete_after=5)
    await asyncio.gather(
        *[send_subscription(bot, channel_id, sub_amount, headers) for _ in range(5)]
    )
    await ctx.message.delete()

bot.run(DISCORD_BOT_TOKEN)
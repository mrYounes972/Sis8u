import json
from telegram import Bot
from config import BOT_TOKEN, OPENAI_API_KEY
import openai

bot = Bot(token=BOT_TOKEN)

def load_channels():
    try:
        with open("channels.json", "r") as f:
            return json.load(f)
    except:
        return []

def add_channel(channel):
    channels = load_channels()
    if channel not in channels:
        channels.append(channel)
        with open("channels.json", "w") as f:
            json.dump(channels, f)

async def check_membership(user_id):
    channels = load_channels()
    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

async def chat_with_gpt(message):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message.content.strip()
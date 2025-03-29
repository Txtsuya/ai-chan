#!/bin/python3

import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks
import tweepy
import os
from datetime import datetime, timezone
import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TWITTER_BASE_URL = "https://twitter.com/sonozvki_/status/"

if not TOKEN:
    raise ValueError("no tokens.")
TWI_API_KEY = os.getenv('TWI_API_KEY')
TWI_API_SECRET = os.getenv('TWI_API_SECRET')

try:
    DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
except (TypeError, ValueError):
    DISCORD_CHANNEL_ID = None

try:
    HSR_TWI_ID = int(os.getenv('HSR_TWI_ID'))
except (TypeError, ValueError):
    HSR_TWI_ID = None
    raise ValueError("HSR_TWI_ID must be an integer.")

TWI_ACCESS_SECRET = os.getenv('TWI_ACCESS_SECRET')
TWI_ACCESS_TOKEN = os.getenv('TWI_ACCESS_TOKEN')

if not TWI_ACCESS_TOKEN:
    raise ValueError("TWI_ACCESS_TOKEN missing.")

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

client = tweepy.Client(
    consumer_key=TWI_API_KEY,
    consumer_secret=TWI_API_SECRET,
    access_token=TWI_ACCESS_TOKEN,
    access_token_secret=TWI_ACCESS_SECRET
)


def load_last_tweet_id():
    try:
        with open('last_tweet.json', 'r') as f:
            data = json.load(f)
            return data.get('last_tweet_id')
    except FileNotFoundError:
        return None


def save_last_tweet_id(tweet_id):
    with open('last_tweet.json', 'w') as f:
        json.dump({'last_tweet_id': tweet_id}, f)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    if not check_tweets.is_running():
        check_tweets.start()
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            print("Error: Invalid or inaccessible channel ID. Please check the DISCORD_CHANNEL_ID and bot permissions.")
            return
        if not channel:
            print("couldn't find the specified channel")
            return

        last_tweet_id = load_last_tweet_id()
        
        try:
            tweets = client.get_users_tweets(
                id=HSR_TWI_ID,
                exclude=['retweets', 'replies'],
                tweet_fields=['created_at'],
                since_id=last_tweet_id
            )
            if not tweets or not tweets.data:
                if tweets and tweets.data:
                    for tweet in tweets.data:
                        tweet_url = f"{TWITTER_BASE_URL}{tweet.id}"
                    created_at = tweet.created_at
                    if created_at and not created_at.tzinfo:
                        created_at = created_at.replace(tzinfo=timezone.utc)

                    if created_at:
                        embed = discord.Embed(
                            title="New Honkai: Star Rail Tweet",
                            url=tweet_url,
                            color=discord.Color.blue(),
                            timestamp=created_at
                        )
                    else:
                        embed = discord.Embed(
                            title="New Honkai: Star Rail Tweet",
                            url=tweet_url,
                            color=discord.Color.blue()
                        )
                        timestamp=created_at
            save_last_tweet_id(str(tweet.id))
        except Exception as e:
            print(f"Error occurred: {e}")

bot.run(TOKEN)
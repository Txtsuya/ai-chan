import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks
import tweepy
import os
from datetime import datetime, timezone
import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TWI_API_KEY = os.getenv('TWI_API_KEY')
TWI_API_SECRET = os.getenv('TWI_API_SECRET')
TWI_ACCESS_TOKEN = os.getenv('TWI_ACCESS_TOKEN')
TWI_ACCESS_SECRET = os.getenv('TWI_ACCESS_SECRET')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
HSR_TWI_ID = os.getenv('HSR_TWI_ID')

intents = discord.Intents.default()
intents.messages = True
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
    check_tweets.start()

@tasks.loop(minutes=5)
async def check_tweets():
    try:
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            print("Couldn't find the specified channel")
            return

        last_tweet_id = load_last_tweet_id()
        
        tweets = client.get_users_tweets(
            id=HSR_TWI_ID,
            exclude=['retweets', 'replies'],
            tweet_fields=['created_at'],
            since_id=last_tweet_id
        )

        if not tweets.data:
            return

        for tweet in reversed(tweets.data):
            tweet_url = f"https://twitter.com/HonkaiStarRail/status/{tweet.id}"
            
            embed = discord.Embed(
                title="New Honkai: Star Rail Tweet",
                url=tweet_url,
                description=tweet.text,
                color=discord.Color.blue(),
                timestamp=tweet.created_at
            )
            embed.set_author(
                name="Honkai: Star Rail Official",
                icon_url="https://pbs.twimg.com/profile_images/1583788321964363776/RBrqVTot_400x400.jpg"
            )
            
            await channel.send(embed=embed)
            
            save_last_tweet_id(str(tweet.id))

    except Exception as e:
        print(f"Error occurred: {e}")

bot.run(TOKEN)
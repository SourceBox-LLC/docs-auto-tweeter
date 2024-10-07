import tweepy

from dotenv import load_dotenv
from gpt import chat_gpt
from docs_scrape import scrape_docs
import os, sys
import json, time

load_dotenv()


# scrape docs to docs.txt
scrape_docs()


# Replace these with your actual credentials
consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
bearer_token = os.getenv('BEARER_TOKEN')

client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
    bearer_token=bearer_token
)


TWEET_LOG_FILE = 'tweet_log.json'
def load_tweet_log():
    """Loads the existing tweet log from a file and returns only the last 20 tweets."""
    if os.path.exists(TWEET_LOG_FILE):
        with open(TWEET_LOG_FILE, 'r') as file:
            tweet_log = json.load(file)
            return tweet_log[-25:]  # Return only the last 20 tweets
    else:
        return []

def save_tweet_log(tweets):
    """Saves the updated tweet log to a file."""
    with open(TWEET_LOG_FILE, 'w') as file:
        json.dump(tweets, file)


def create_tweet(text):
    response = client.create_tweet(text=text)
    save_tweet_log(response)
    return response


tweet_log = load_tweet_log()
gpt_response = chat_gpt(tweet_log)
create_tweet(gpt_response)
print("Tweet created successfully")
    
time.sleep(5)

tweet_log2 = load_tweet_log()
gpt_response2 = chat_gpt(tweet_log2)
create_tweet(gpt_response2)
print("Tweet created successfully")
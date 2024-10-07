import tweepy
from dotenv import load_dotenv
from gpt import chat_gpt, image_gen
from docs_scrape import scrape_docs
import os, sys
import json, time, random

load_dotenv()


image = image_gen("Easily connect your data to AI with PackMan! Transfer files from local, web, AWS, and more. Elevate your AI projects with personalized data packs. 📦 #PackMan https://sourcebox.cloud")
print(image)

sys.exit()

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
    """Loads the existing tweet log from a file and returns only the last 25 tweets."""
    if os.path.exists(TWEET_LOG_FILE):
        with open(TWEET_LOG_FILE, 'r') as file:
            tweet_log = json.load(file)
            return tweet_log[-25:]  # Return only the last 25 tweets
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


# Set daily tweet count options and pick a random number for today
daily_posts = [2, 3]  # Number of tweets to post each day (random choice between 2 and 3)
random_daily = random.choice(daily_posts)

# Create tweets based on the randomly chosen number
for _ in range(random_daily):

    # Set random sleep intervals between tweets (in seconds)
    sleep_intervals = [10, 20, 40, 80, 100, 1200]  # Sleep intervals in seconds
    random_sleep = random.choice(sleep_intervals)

    # Wait for a random amount of time before posting the next tweet
    print(f"Sleeping for {random_sleep} seconds before the next tweet...")
    time.sleep(random_sleep)

    # Load the tweet log and get a GPT-generated response
    tweet_log = load_tweet_log()
    gpt_response = chat_gpt(tweet_log)

    # Create and post the tweet
    create_tweet(gpt_response)
    print("Tweet created successfully")

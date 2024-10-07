import tweepy
from dotenv import load_dotenv
from gpt import chat_gpt, image_gen
from docs_scrape import scrape_docs
import os, sys
import json, time, random
import re

load_dotenv()

# Scrape docs to docs.txt
scrape_docs()

# Replace these with your actual credentials
consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
bearer_token = os.getenv('BEARER_TOKEN')

# Tweepy client initialization
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
    try:
        if os.path.exists(TWEET_LOG_FILE):
            with open(TWEET_LOG_FILE, 'r') as file:
                tweet_log = json.load(file)
                return tweet_log[-25:]  # Return only the last 25 tweets
        else:
            return []
    except json.JSONDecodeError:
        print("Error reading the tweet log. Returning an empty log.")
        return []

def save_tweet_log(tweets):
    """Saves the updated tweet log to a file."""
    try:
        with open(TWEET_LOG_FILE, 'w') as file:
            json.dump(tweets, file)
    except Exception as e:
        print(f"Error saving tweet log: {e}")

def is_valid_url(url):
    """Check if a given URL is valid."""
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return re.match(url_pattern, url) is not None

def sanitize_tweet(text):
    """Remove invalid URLs from the tweet text."""
    words = text.split()
    sanitized_words = [word if not word.startswith("http") or is_valid_url(word) else "[Invalid URL Removed]" for word in words]
    return " ".join(sanitized_words)

def create_tweet(text):
    """Create a tweet and handle potential errors."""
    try:
        text = sanitize_tweet(text)
        print(f"Attempting to post tweet: {text}")  # Debugging output
        response = client.create_tweet(text=text)
        save_tweet_log([response.data])  # Save only the tweet data to the log
        print("Tweet created successfully")
        return response
    except tweepy.errors.BadRequest as e:
        print(f"BadRequest Error: {e}")
        print("The tweet contains an invalid URL or is malformed. Attempting to fix...")
        # Remove invalid URLs and try again
        text = sanitize_tweet(text)
        try:
            response = client.create_tweet(text=text)
            save_tweet_log([response.data])
            print("Tweet created successfully after correction.")
            return response
        except Exception as second_try_error:
            print(f"Failed to create tweet after correction: {second_try_error}")
            return None
    except Exception as e:
        print(f"An error occurred while creating tweet: {e}")
        return None

# Set daily tweet count options and pick a random number for today
daily_posts = [2, 3]  # Number of tweets to post each day (random choice between 2 and 3)
random_daily = random.choice(daily_posts)

# Create tweets based on the randomly chosen number
for _ in range(random_daily):

    # Set random sleep intervals between tweets (in seconds)
    #sleep_intervals = [10, 20, 40, 80, 100, 120]  # Sleep intervals in seconds
    sleep_intervals = [1, 2]
    random_sleep = random.choice(sleep_intervals)

    # Wait for a random amount of time before posting the next tweet
    print(f"Sleeping for {random_sleep} seconds before the next tweet...")
    time.sleep(random_sleep)

    # Load the tweet log and get a GPT-generated response
    try:
        tweet_log = load_tweet_log()
        gpt_response = chat_gpt(tweet_log)
        print(f"GPT response generated: {gpt_response}")

        # Create and post the tweet
        create_tweet(gpt_response)
    except Exception as e:
        print(f"Error generating or posting tweet: {e}")

from openai import OpenAI
import os
from dotenv import load_dotenv
import random
import requests
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()

search = DuckDuckGoSearchRun()

def doc_content():
    with open('docs.txt', 'r', encoding='utf-8') as file:
        return file.read()

# Define some random modifiers for tweet variety
tweet_styles = ["informative", "promotional", "exciting", "engaging", "casual"]

# Choose a random style for this tweet
random_style = random.choice(tweet_styles)

# Define hashtag amount and choose a random number
hashtag_ammount = [1, 2, 3, 4]
random_number = random.choice(hashtag_ammount)


client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY')
    )


def topics():
    topics = ['tips', 'news', 'trends', 'fun facts', 'Motivational', 'engagement question']

    random_topic = random.choice(topics)

    if random_topic == 'tips':
        instructions = 'Create a random AI tip post.'

    elif random_topic == 'news':
        news = search.invoke("What is the latest news in AI?")
        instructions = f'Create a post about the latest AI news here: {news}.'

    elif random_topic == 'trends':
        news = search.invoke("What is the latest news in AI?")
        instructions = f'Share some trending topic in the AI or tech space: {news}.'

    elif random_topic == 'fun facts':
        instructions = 'Post a fun fact about AI, technology, or startups.'

    elif random_topic == 'Motivational':
        instructions = 'Share a motivational quote or thought for entrepreneurs and developers.'
        
    elif random_topic == 'engagement question':
        instructions = 'Ask a question to engage your audience (e.g., "What’s your favorite AI tool?").'

    return instructions

def chat_gpt(tweets):

    # Reformat previous tweets into a structured list to give the model better context
    formatted_tweets = "\n".join([f"- {tweet}" for tweet in tweets])

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f'''
                            You are a Twitter social media manager for the tech startup 'SourceBox LLC'. 
                            All responses must be 200 characters or less. You must follow a unique style for each tweet.

                            Current style: {random_style}.
                            Current subject: {topics()}
                            

                            Your tweets must be unique and must not be similar to any of the previous tweets listed here:
                            {formatted_tweets}.

                            You must use exactly {random_number} relevant hashtag(s) that match the current style and context.'''
            },
            {
                "role": "user",
                "content": f"Generate a tweet. Here is the history of our previous tweets:\n{formatted_tweets}",
            }
        ],
        model="gpt-4",
    )

    # Access the content using the 'message' attribute of the Choice object
    assistant_message = chat_completion.choices[0].message.content

    return assistant_message






def image_gen(tweet, filename="generated_image.png"):
    """Generate an image using OpenAI's DALL-E model and save it as a local file."""
    try:
        # Generate the image using OpenAI's DALL-E
        response = client.images.generate(
            model="dall-e-3",
            prompt=tweet,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Check if the response contains the generated image URL
        if not response or "data" not in response or len(response["data"]) == 0:
            print("Error: No image URL returned by OpenAI.")
            return None

        # Extract the image URL from the response
        image_url = response["data"][0]["url"]

        # Download the image and save it as a file
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            with open(filename, 'wb') as file:
                file.write(image_response.content)
            print(f"Image saved successfully as {filename}")
        else:
            print(f"Failed to download the image. Status code: {image_response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred while generating or downloading the image: {e}")
        return None

    return filename  # Return the filename of the saved image

from openai import OpenAI
import os
from dotenv import load_dotenv
import random
import requests

load_dotenv()

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
                            Your tweets must be in the scope of the SourceBox documentation here: {doc_content()}.
                            Your tweets must be unique and must not be similar to any of the previous tweets listed here:
                            {formatted_tweets}.
                            Use exactly {random_number} relevant hashtag(s) that match the current style and context.'''
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
    """Generate an image using OpenAI's DALL-E and save it as a file."""
    response = client.images.generate(
        model="dall-e-3",
        prompt=tweet,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    # Get the image URL from the response
    image_url = response.data[0].url

    # Download the image and save it as a file
    image_response = requests.get(image_url)
    if image_response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(image_response.content)
        print(f"Image saved successfully as {filename}")
    else:
        print(f"Failed to download the image. Status code: {image_response.status_code}")
    
    return filename  # Return the filename of the saved image

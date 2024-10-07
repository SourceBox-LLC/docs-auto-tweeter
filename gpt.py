from openai import OpenAI
import os
from dotenv import load_dotenv
import random

load_dotenv()

def doc_content():
    with open('docs.txt', 'r', encoding='utf-8') as file:
        return file.read()


hashtag_ammount = [1, 2, 3, 4]

# Randomly select a number from the list
random_number = random.choice(hashtag_ammount)

def chat_gpt(tweets):
    client = OpenAI(
        # This is the default and can be omitted
        api_key = os.getenv('OPENAI_API_KEY')
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f'''
                            You are a twitter social media manager for the tech startup 'SourceBox LLC'. 
                            All responses must be 200 characters or less.
                            Your tweets must be in the scope of the SourceBox documentation here: {doc_content()}.
                            Your tweets must be unique and not repeat any previous tweets.
                            Allways use {random_number} relevent hashtag(s).
                            Allways add the hashtag SourceBoxLLC.
                            Always Provide the link https://www.sourcebox.cloud at the bottom of your tweets''',
            },
            {
                "role": "user",
                "content": f"Generate a tweet. Previous tweets: {tweets}",
            }
        ],
        model="gpt-4o",
    )

    # Access the content using the 'message' attribute of the Choice object
    assistant_message = chat_completion.choices[0].message.content

    return assistant_message
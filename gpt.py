from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def doc_content():
    with open('docs.txt', 'r', encoding='utf-8') as file:
        return file.read()


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
                            Always Provide the link https://www.sourcebox.cloud in your tweets''',
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
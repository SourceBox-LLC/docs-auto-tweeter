import logging
from dotenv import load_dotenv
import os
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import tweepy
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.messages import SystemMessage
from docs_scrape import scrape_docs, query_docs
import psycopg2

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Initialize memory and model
memory = MemorySaver()
model = ChatOpenAI(model="gpt-4")

# Initialize search tool
search = TavilySearchResults(max_results=2)

# Create an OpenAI client
client = OpenAI()


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

def Agent(user_prompt):
    logging.info(f"Agent started with prompt: {user_prompt}")

    # Dall-E Image Generation Tool
    @tool
    def generate_image(prompt: str) -> str:
        """Generate an image"""
        response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        )
        image_url = response.data[0].url
        logging.info(f"Generated image URL: {image_url}")
        return image_url


    # search the sourcebox docs
    @tool
    def sourcebox_docs(prompt: str) -> str:
        """Search the Sourcebox docs."""
        db = scrape_docs()
        results = query_docs(db, prompt)
        logging.info(f"Sourcebox docs search results: {results}")
        return results

    # can take a prompt and create a tweet
    @tool
    def create_tweet(prompt: str) -> str:
        """Create a tweet and handle potential errors."""
        try:
            logging.info(f"Attempting to post tweet: {prompt}")
            response = client.create_tweet(text=prompt)
            logging.info("Tweet created successfully")
            return response
        except tweepy.errors.BadRequest as e:
            logging.error(f"BadRequest Error: {e}")
            return e
        except Exception as e:
            logging.error(f"An error occurred while creating tweet: {e}")
            return e

    # get the latest platform updates
    @tool
    def platform_updates():
        """Get the latest platform updates."""
        loader = WebBaseLoader("https://www.sourcebox.cloud/updates")
        documents = loader.load()
        logging.info(f"Loaded platform updates: {documents}")
        return documents

    # Tool assignments
    tools = [generate_image, search, create_tweet, sourcebox_docs, platform_updates]

    logging.info("____________CUSTOM TOOL PROPERTIES______________")
    # Inspect some of the attributes associated with generate_image
    logging.info(generate_image.name)
    logging.info(generate_image.description)
    logging.info(generate_image.args)

    # Inspect some of the attributes associated with create_tweet
    logging.info(create_tweet.name)
    logging.info(create_tweet.description)
    logging.info(create_tweet.args)

    # Inspect some of the attributes associated with sourcebox_docs
    logging.info(sourcebox_docs.name)
    logging.info(sourcebox_docs.description)
    logging.info(sourcebox_docs.args)

    # Inspect some of the attributes associated with platform_updates
    logging.info(platform_updates.name)
    logging.info(platform_updates.description)
    logging.info(platform_updates.args)

    logging.info("____________END CUSTOM TOOL PROPERTIES______________")

    logging.info("____________AGENT CREATION______________")

    # Create the agent
    agent_executor = create_react_agent(
        model, 
        tools,
        checkpointer=memory
    )

    # Use the agent
    config = {"configurable": {"thread_id": "abc123"}}

    # Define the system prompt
    system_prompt = f"""
    You are the lead social media manager for SourceBox LLC with access to tools for creating tweets. 
    Your job is to:
    1. tweet about the latest platform updates.
    2. advertise services from the documentation
    3. create and tweet a step by step user tutorial using information from the documentation.
    4. tweet about the benefits of using SourceBox
    5. tweet about AI news and fun facts using internet search tool

    RULES:
    be engaging and creative. stick to the facts.
    Cover all range of topics in the documentation.
    when covering news be direct and informative. no advertising.
    all tweets must be no more than 280 characters. That is the twitter limit.
    make no more than 2 tweets.
    """


    if user_prompt == "":
        user_prompt = "No user prompt provided. tweet on your own following the system prompt. pick a topic from the list."

    prompt = f"""
    SYSTEM PROMPT: {system_prompt}
    USER PROMPT: {user_prompt}\n"""


    for chunk in agent_executor.stream(
        {"messages": [HumanMessage(content=prompt)]}, config
    ):
        logging.info(f"Agent response chunk: {chunk}")
        yield chunk

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import DeepLake
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from dotenv import load_dotenv
import logging

load_dotenv()


def scrape_docs():
    # Load the document from the URL
    loader = WebBaseLoader("https://www.sourcebox.cloud/docs")
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    try:
        embeddings = OpenAIEmbeddings()
        db = DeepLake(dataset_path="./my_deeplake/", embedding=embeddings, overwrite=True)
        db.add_documents(docs)
    except Exception as e:
        from langchain_huggingface import HuggingFaceEmbeddings

        if "rate limit" in str(e).lower() or "429" in str(e):
            logging.warning("OpenAI rate limit exceeded, switching to HuggingFace embeddings.")
            # Fallback to Anthropic embeddings
            embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
            db = DeepLake(dataset_path="./my_deeplake/", embedding=embeddings_model, overwrite=True)
            db.add_documents(docs)
        else:
            raise e

    return db  # Return the db object


def query_docs(db, prompt):
    docs = db.similarity_search(prompt)
    return docs


if __name__ == "__main__":
    # Call scrape_docs to get the db object
    db = scrape_docs()

    # Use the db object in query_docs
    query = query_docs(db, "What is the sourcelightning service?")
    print(query)

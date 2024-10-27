from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import DeepLake
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()


def scrape_docs():
    # Load the document from the URL
    loader = WebBaseLoader("https://www.sourcebox.cloud/docs")
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()

    db = DeepLake(dataset_path="./my_deeplake/", embedding=embeddings, overwrite=True)
    db.add_documents(docs)

    return db  # Return the db object


def query_docs(db, prompt):
    docs = db.similarity_search(prompt)
    return docs



# Call scrape_docs to get the db object
db = scrape_docs()

# Use the db object in query_docs
query = query_docs(db, "What is the sourcelightning service?")
#print(query)

from langchain_community.document_loaders import WebBaseLoader


def scrape_docs():
    # Load the document from the URL
    loader = WebBaseLoader("https://www.sourcebox.cloud/docs")
    docs = loader.load()

    # Get the content from the first document
    content = docs[0].page_content

    # Define the output file path
    output_file = "docs.txt"

    # Write the content to the file, overwriting any existing content
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(content)

    print(f"Content written to {output_file} successfully.")

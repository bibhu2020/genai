import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import time

# db path
persist_directory="/mnt/c/Users/v-bimishra/workspace/srescripts/pocs/genai/_vectordbs/ragapp_db"

def scrape_website(start_url, max_pages=100):
    visited = set()
    to_visit = [start_url]
    documents = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text content
            text = soup.get_text(separator=' ', strip=True)
            documents.append({"url": url, "content": text})

            # Find new links
            for link in soup.find_all('a', href=True):
                new_url = urljoin(url, link['href'])
                if new_url.startswith(start_url) and new_url not in visited:
                    to_visit.append(new_url)

            visited.add(url)
            print(f"Scraped: {url}")
            time.sleep(1)  # Respect the website by adding a delay

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    return documents

def embed_and_store(documents):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vectorstore = Chroma(embedding_function=embeddings, persist_directory=persist_directory)

    for doc in documents:
        vectorstore.add_texts(
            texts=[doc["content"]],
            metadatas=[{"url": doc["url"]}]
        )

    # vectorstore.persist()
    print("All documents have been embedded and stored in ChromaDB.")

# Usage
start_url = "https://langchain.com"  # Replace with the website you want to scrape
scraped_docs = scrape_website(start_url)
embed_and_store(scraped_docs)

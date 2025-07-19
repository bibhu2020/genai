import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
#from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# db path
persist_directory="/mnt/c/Users/v-bimishra/workspace/srescripts/pocs/genai/_vectordbs/ragapp_db"

# Specify the folder containing PDF files
pdf_folder = "/mnt/c/Users/v-bimishra/workspace/srescripts/pocs/genai/_data/rag_input"


# Set up the embeddings model
#embeddings = OllamaEmbeddings(model="gemma:2b")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Initialize the vector store
vectorstore = Chroma(embedding_function=embeddings, persist_directory=persist_directory)

# Set up the text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)

# Loop through the folder
for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        file_path = os.path.join(pdf_folder, filename)
        print(f"Processing: {filename}")
        
        # Load the PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Split the document into chunks
        chunks = text_splitter.split_documents(documents)
        
        # Add the chunks to the vector store
        vectorstore.add_documents(chunks)

# # Persist the vector store
# vectorstore.persist() #it auto stores

print("All PDF files have been processed and stored in the vector database.")

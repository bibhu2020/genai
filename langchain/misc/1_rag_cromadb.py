## A RAG (Retrieval Augmented Generation) Application using Langchain
## It creates embeddings from PDF documents and stores them in a vector database (chromadb).
## It uses the RAG model to answer questions based on the vector database.
## 1_rag_vector.py is the first part of the application that creates the transcripts and stores them in a vector database.
## 2_rag_vector.py is the second part of the application that uses the RAG model to answer questions based on the transcripts.

## It uses the langchain whisper class to create transcripts from YouTube videos. 
## Whisper represents OpenAI's Whisper model which is an automatic speech recognition (ASR) model that converts speech to text.
## pip install git+https://github.com/openai/whisper.git
## You can use Azure Speech-to-Text, Google Cloud Speech-to-Text, or any other ASR model to create transcripts also.

import os
import shutil
from pathlib import Path
import pprint
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utility.embedding_factory import EmbeddingFactory
from langchain.utility.llm_factory2 import LLMFactory
from langchain.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from langchain.agents import initialize_agent, Tool
from typing import List, Any


def load_pdf_to_docs(file_path: str) -> List[Any]:
    try:
        pdf_loader = PyPDFLoader(file_path)
        docs = pdf_loader.load()
        #print(f"Successfully loaded {len(docs)} documents from {file_path}.")
        return docs
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return []
 
def load_msdocs_to_docs(file_path: str):
    """
    Load a Microsoft Office files and convert its content into a list of documents.
    """
    try:
        pptx_loader = UnstructuredPowerPointLoader(file_path)
        docs = pptx_loader.load()
        # print(f"Successfully loaded {len(docs)} slides from {file_path}.")
        return docs
    except Exception as e:
        print(f"Error loading Microsoft Office file: {e}")
        return []
    
def load_txt_to_docs(file_path: str):
    """
    Load a TXT file and convert its content into a list of documents.
    """
    try:
        txt_loader = TextLoader(file_path)
        docs = txt_loader.load()
        #print(f"Successfully loaded {len(docs)} documents from {file_path}.")
        return docs
    except Exception as e:
        print(f"Error loading TXT: {e}")
        return []
    
def split_docs_to_chunks(docs: list):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=20
        )
        chunks = text_splitter.split_documents(docs)
        #print(f"Successfully split {len(docs)} documents into {len(chunks)} chunks.")
        return chunks
    except Exception as e:
        print(f"Error splitting documents: {e}")
        return []
    
def create_vector_db(llm_embedder: object, chunks: list, db_path: str):
    try:
        # if os.path.exists(f"{db_path}"):
        #     shutil.rmtree(f"{db_path}") # Delete the directory if it already exists

        from langchain_chroma import Chroma
        db = Chroma.from_documents(
            documents=chunks,
            embedding=llm_embedder,
            persist_directory=f"{db_path}"
        )
        #print(f"Successfully created vector database at {db_path}.")
        return db
    except Exception as e:
        print(f"Error creating vector database: {e}")
        return None
    
class PDFProcessor(BaseTool):
    """
    A custom tool to create embeddings from PDF and store in vector db.
    """
    name: str = "process_pdf"  # Added type annotation
    description: str = "Creates embeddings from PDF and store in vector db."  # Added type annotation

    def _run(self, file_path: str):
        llm_embedder = EmbeddingFactory.get_llm("azure")
        docs = load_pdf_to_docs(file_path)
        chunks = split_docs_to_chunks(docs)
        # load the chunks into the vector database
        db = create_vector_db(llm_embedder, chunks, f"{db_file_path}")
        return db
    
    def _arun(self, file_path: str) -> None:
        raise NotImplementedError("Asynchronous processing is not supported.")

class TXTProcessor(BaseTool):
    """
    A custom tool to create embeddings from TXT and store in vector db.
    """
    name: str = "process_txt"  # Added type annotation
    description: str = "Creates embeddings from TXT and store in vector db."  # Added type annotation

    def _run(self, file_path: str):
        llm_embedder = EmbeddingFactory.get_llm("azure")
        docs = load_txt_to_docs(file_path)
        chunks = split_docs_to_chunks(docs)
        # load the chunks into the vector database
        db = create_vector_db(llm_embedder, chunks, f"{db_file_path}")
        return db
    
    def _arun(self, file_path: str) -> None:
        raise NotImplementedError("Asynchronous processing is not supported.")

class UnstructuredProcessor(BaseTool):
    """
    A custom tool to create embeddings from Microsoft Docs & ppts and store in vector db.
    """
    name: str = "process_unstructured"  # Added type annotation
    description: str = "Creates embeddings from PPTX/DOCX and store in vector db."  # Added type annotation

    def _run(self, file_path: str):
        llm_embedder = EmbeddingFactory.get_llm("azure")
        docs = load_msdocs_to_docs(file_path)
        chunks = split_docs_to_chunks(docs)
        # load the chunks into the vector database
        db = create_vector_db(llm_embedder, chunks, f"{db_file_path}")
        return db
    
    def _arun(self, file_path: str) -> None:
        raise NotImplementedError("Asynchronous processing is not supported.")

if __name__ == "__main__":
    # Input and archive directories
    input_directory = "/mnt/c/Users/v-bimishra/workspace/aksscripts/_nonaks/azureai/langchain/_data/input"
    archive_directory = "/mnt/c/Users/v-bimishra/workspace/aksscripts/_nonaks/azureai/langchain/_data/archive" 
    db_file_path = "/mnt/c/Users/v-bimishra/workspace/aksscripts/_nonaks/azureai/cromadb/db1"
    llm_embedder = EmbeddingFactory.get_llm("azure")
    llm = LLMFactory.get_llm("azure")
    
    # Create archive directory if it doesn't exist
    Path(archive_directory).mkdir(parents=True, exist_ok=True)   

    # Loop through PDF files in the input directory
    for file_name in os.listdir(input_directory):
        file_path = os.path.join(input_directory, file_name)

        # Check if the file is a PDF
        if os.path.isfile(file_path) :  #and file_name.endswith(".pdf")
            print(f"Processing: {file_name}")
            
            # # Process the file
            # # split the PDF into documents and then into chunks
            # docs = load_pdf_to_docs(file_path)
            # chunks = split_docs_to_chunks(docs)
            # # load the chunks into the vector database
            # db = create_vector_db(llm_embedder, chunks, f"{db_file_path}")

            # Create the PDFProcessor
            pdf_loader_tool = PDFProcessor()
            txt_loader_tool = TXTProcessor()
            unstructured_loader_tool = UnstructuredProcessor()
            # Define the tool list
            tools = [pdf_loader_tool, txt_loader_tool, unstructured_loader_tool]
            # Prompt to guide the agent
            prompt = PromptTemplate(
                input_variables=["file_path"],
                template="You are a document embedding assistant. Use the tools available to process PDF, DOCX, PPTX & TXT files. The file path is {file_path}."
            )

            # Initialize the agent
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent="zero-shot-react-description",
                verbose=True
            )

            response = agent.invoke(f"Process the PDF/TXT/DOCX/PPTX from this path: {file_path}")
            print(response)

            # Move the processed file to the archive directory
            archive_path = os.path.join(archive_directory, file_name)
            shutil.move(file_path, archive_path)

            # Optionally remove the original file after processing
            print(f"Moved to archive: {archive_path}")


import logging
import autogen
from utility.llm_config import LLMConfig

# Setup logging
logging.basicConfig(level=logging.INFO)

llm_manager = LLMConfig(
    seed=42,
    temperature=0,
    is_azure_open_ai=True,
    model_name="gpt-4"
)
# Get the configuration for autogen
llm_config = llm_manager.llm_config

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utility.embedding_factory import EmbeddingFactory
from utility.llm_factory import LLMFactory
from langchain_chroma import Chroma
from pydantic import BaseModel, Field
from typing import Annotated
from pathlib import Path
import os
from typing import List, Any
   
## Define Custom Tools
class FileLocatorInput(BaseModel):
    input_dir: Annotated[str, Field(description="Input Directory.")]

def file_locator_tool(input: Annotated[FileLocatorInput, "Locate the file."]) -> str:
    file_path = ""
    for file_name in os.listdir(input.input_dir):
        file_path = os.path.join(input.input_dir, file_name)
        break;
    
    return file_path

class PDFLoaderInput(BaseModel):
    file_path: Annotated[str, Field(description="Input File Path.")]

def pdf_loader_tool(input: Annotated[PDFLoaderInput, "Load PDF file."]) -> List[Any]:
    try:
        pdf_loader = PyPDFLoader(input.file_path)
        docs = pdf_loader.load()
        print(f"Successfully loaded {len(docs)} documents from {input.file_path}.")
        return docs
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return []
    
class DocumentSplitterInput(BaseModel):
    docs: Annotated[List[Any], Field(description="Documents.")]

def document_splitter_tool(input: Annotated[DocumentSplitterInput, "Split the document into chunks"]) -> List[Any]:
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=20
        )
        chunks = text_splitter.split_documents(input.docs)
        #print(f"Successfully split {len(docs)} documents into {len(chunks)} chunks.")
        return chunks
    except Exception as e:
        print(f"Error splitting documents: {e}")
        return []
    
class StoreChunksInput(BaseModel):
    chuck: Annotated[List[Any], Field(description="Chunks.")]
    db_path: Annotated[str, Field(description="DB File Path.")]
    
def store_chunks_tool(input: Annotated[StoreChunksInput, "Create chunk embeddings and store into vector database."]) -> str:
    try:
        # if os.path.exists(f"{db_path}"):
        #     shutil.rmtree(f"{db_path}") # Delete the directory if it already exists
        llm_embedder = EmbeddingFactory.get_llm("azure")
        from langchain_chroma import Chroma
        db = Chroma.from_documents(
            documents=input.chunks,
            embedding=llm_embedder,
            persist_directory=f"{input.db_path}"
        )
        #print(f"Successfully created vector database at {db_path}.")
        return (f"Successfully stored the chunks.")
    except Exception as e:
        print(f"Error creating vector database: {e}")
        return (f"Error creating vector database: {e}")


# Define the Assistants
file_locator_assistant = autogen.ConversableAgent(
    name="file_locator",
    llm_config=llm_config,
    system_message="""
    You are an AI assistant responsible for monitoring an input folder.  
    Your tasks are as follows:  
    1. Continuously watch the input folder for new files.  
    - Only consider files with `.pdf` extensions.  

    2. When a new file is detected:  
    - Send the file path to the pdf loader assistant for processing, one file at a time.  

    3. If the folder remains empty for an extended period, reply with **TERMINATE**
    """
)

pdf_loader_assistant = autogen.ConversableAgent(
    name="pdf_loader",
    llm_config=llm_config,
    system_message="""
    You are an AI assistant responsible for loading the input pdf and creating documents.
    """
)

document_splitter_assistant = autogen.ConversableAgent(
    name="document_splitter",
    llm_config=llm_config,
    system_message="""
    You are an AI assistant responsible for splitting the document into chunks.
    """
)

store_chunks_assistant = autogen.ConversableAgent(
    name="store_chunks",
    llm_config=llm_config,
    system_message="""
    You are an AI assistant responsible for chunk embeddings and storing them into vector database.
    """
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config=False, #{"work_dir": "code", "use_docker": False},
    llm_config=llm_config,
    system_message="""
    You are a User Proxy responsible for facilitating communication between the assistants to create embeddings from the input files and store them into vector database.  
    Your tasks are as follows:  

    1. You can send messages to the assistants and execute code & install modules to help accomplish the assigned tasks.  

    2. Respond appropriately based on task progress:  
    - If the code looks satisfactory, reply with **TERMINATE**.  
    - If the code is incomplete, reply with **CONTINUE** or provide a clear explanation of why the code is not yet right.  

    Your objective is to ensure working code is generated efficiently."""
)

# Register the tools with the assistants
file_locator_assistant.register_for_llm(name="file_locator_tool", description="Monitors folder for files.")(file_locator_tool)
pdf_loader_assistant.register_for_llm(name="pdf_loader_tool", description="Loads the pdf file.")(pdf_loader_tool)
document_splitter_assistant.register_for_llm(name="document_splitter_tool", description="Split document into chunks.")(document_splitter_tool)
file_locator_assistant.register_for_llm(name="store_chunks_tool", description="Stores chunk embeddings into vector database.")(store_chunks_tool)
user_proxy.register_for_execution(name="file_locator_tool")(file_locator_tool)
user_proxy.register_for_execution(name="pdf_loader_tool")(pdf_loader_tool)
user_proxy.register_for_execution(name="document_splitter_tool")(document_splitter_tool)
user_proxy.register_for_execution(name="store_chunks_tool")(store_chunks_tool)

from autogen import GroupChat

group_chat_with_introductions  = GroupChat(
    agents=[file_locator_assistant, pdf_loader_assistant, document_splitter_assistant, store_chunks_assistant, user_proxy],
    messages=[],
    max_round=6,
    send_introductions=True,
)

from autogen import GroupChatManager

group_chat_manager = GroupChatManager(
    groupchat=group_chat_with_introductions,
    llm_config=llm_config
)

# Define task
input_dir = Path("/mnt/c/Users/v-bimishra/workspace/srescripts/pocs/genai/langchain/_data/input")
archive_dir = Path("/mnt/c/Users/v-bimishra/workspace/srescripts/pocs/genai/langchain/_data/archive")
db_dir = "/mnt/c/Users/v-bimishra/workspace/srescripts/pocs/genai/cromadb/db2"
task = f"""
Watch the input folder {input_dir}. 
When you see files, send them to the document_processor for processing in a loop.
On every successful processing of the file, move the file to the archive folder {archive_dir}.
"""

try:
    # Initiate chat
    logging.info("Initiating chat...")
    chat_result = user_proxy.initiate_chats(
        [
            {
                "recipient": group_chat_manager,
                "message": task,
            }
        ]
    )
    logging.info(f"Chat result: {chat_result}")
except Exception as e:
    logging.error(f"An error occurred: {e}")
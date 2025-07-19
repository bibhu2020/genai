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
from typing import Any, Dict
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from utility.embedding_factory import EmbeddingFactory
from langchain.utility.llm_factory2 import LLMFactory

def initialize_vectorstore(llm_embedder: Any, chroma_persist_directory: str) -> Chroma:
    return Chroma(
        persist_directory=chroma_persist_directory,
        embedding_function=llm_embedder
    )

def build_qa_chain(llm: Any, vectorstore: Chroma) -> RetrievalQA:
    # Create custom prompt template
    prompt_template = """Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know. Don't try to make up an answer.
    
    Context:
    {context}
    
    Question: {question}
    """
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # Create RetrievalQA chain. It chains the LLM with a retriever.
    ## It creates embedding of the query, sends it to the retriever, and retrieves the top-k documents.
    ## It then sends the documents & query to the LLM to generate the answer.
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    return qa_chain

def query_pdf_app(llm: Any, llm_embedder: Any, chroma_persist_directory: str, query: str) -> Dict:
    vectorstore = initialize_vectorstore(llm_embedder, chroma_persist_directory)
    qa_chain = build_qa_chain(llm, vectorstore)
    try:
        response = qa_chain.invoke({"query": query})
        return {
            "answer": response["result"],
            "source_docs": [doc.metadata for doc in response["source_documents"]]
        }
    except Exception as e:
        return {"error": f"Error processing query: {str(e)}"}

if __name__ == "__main__":
    llm = LLMFactory.get_llm("azure")
    llm_embedder = EmbeddingFactory.get_llm("azure")
    chroma_persist_directory = "/mnt/c/Users/v-bimishra/workspace/aksscripts/_nonaks/azureai/cromadb/db1"
    
    while True:
        query = input("\nEnter your question (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
            
        result = query_pdf_app(llm, llm_embedder, chroma_persist_directory, query)
        
        if "error" in result:
            print(f"\nError: {result['error']}")
        else:
            print("\nAnswer:", result["answer"])
            # print("\nSources:")
            # for doc in result["source_docs"]:
            #     print(f"- Source: {doc.get('source', 'Unknown')}")
            #     print(f"  Page: {doc.get('page', 'Unknown')}")
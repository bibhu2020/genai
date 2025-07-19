import streamlit as st
from langchain_chroma import Chroma
#from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA


# db path
persist_directory="/mnt/c/Users/v-bimishra/workspace/srescripts/pocs/genai/_vectordbs/ragapp_db"

# Initialize embeddings and vector store
#embeddings = OllamaEmbeddings(model="gemma:2b")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

# Retriever (a layer on top of vector db that simplified querying vector db)
retriver=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

# Initialize LLM
# llm = OllamaLLM(model="gemma:2b")
llm = ChatOpenAI(model="gpt-4o")

prompt = ChatPromptTemplate.from_template(
    """
    Use the following pieces of context to answer the question at the end. 
    If you don't see the relevant content in the context, just say that you don't know. Don't try to make up an answer.
    
    Context:
    {context}
    
    Question: {question}

    """
)


qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

# Streamlit app
st.title("Document Q&A System")

# User input
query = st.text_input("Enter your question:")

if query:
    response = qa_chain.invoke({"query": query})
    st.write("Answer:", response['result'])

# streamlit run app.py

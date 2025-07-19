## A Q&A Application built on ollama and streamlit

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import streamlit as st

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert AI Engineer. Provide me answer based on the question."),
        ("user", "{question}")
    ]
)

## streamlit framework
st.title("Langchain Demo with Google Gemma Model")
input_text=st.text_input("What's your question?")

## llm client
llm = OllamaLLM(model="gemma:2b")

# Parser
parser = StrOutputParser()
chain = prompt | llm | parser

if input_text:  
    response = chain.invoke({"question":input_text})
    st.write(response)

# streamlit run 06-ollama-QnA-app.py
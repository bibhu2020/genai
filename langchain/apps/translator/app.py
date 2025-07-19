import os
from fastapi import FastAPI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langserve import add_routes

llm_groq = ChatGroq(model="gemma2-9b-it", groq_api_key=os.getenv("GROQ_API_KEY"))

parser = StrOutputParser()

generic_template = "Translate the following content from english into {language}. Keep the language formal."
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", generic_template),
        ("user", "{text}")
    ]
)

# create chain
chain = prompt | llm_groq | parser

## App Definition
app=FastAPI(title="Langchain Server", version="1.0", descrption="A simple API server using langchain runnable interface")

add_routes(
    app,
    chain,
    path="/chain"
)

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="localhost",port=8080)
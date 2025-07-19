import os
from fastapi import FastAPI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langserve import add_routes

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..'))
from utility.llm_factory import LLMFactory


# print(os.environ) 

# print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))

# llm = ChatGroq(model="gemma2-9b-it", groq_api_key=os.getenv("GROQ_API_KEY"))

llm = LLMFactory.get_llm("groq")
parser = StrOutputParser()

generic_template = "Translate the following content from english into {language}. Keep the language formal."
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", generic_template),
        ("user", "{text}")
    ]
)

# create chain
chain = prompt | llm | parser

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
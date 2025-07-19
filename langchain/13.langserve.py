from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


from langchain_groq import ChatGroq
llm = ChatGroq(model="Gemma2-9b-It", max_tokens=512)


from langserve import add_routes


app = FastAPI(title="LangChain Groq LLM Application",
              description="A simple FastAPI application using LangChain with Groq LLM.",
              version="0.1.0",
              openapi_url="/groq/openapi.json",
              docs_url="/groq/docs",
              redoc_url="/groq/redoc")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", "{question}"),
    ]
)
chain = prompt | llm | StrOutputParser()    

add_routes(
    app,
    chain,
    path="/groq"
)

# Uncomment the lines below to run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)



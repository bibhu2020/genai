# Ollama LLM application example
## This example demonstrates how to use the Ollama LLM application with LangChain.

# from langchain_ollama import Ollama
# from langhcinain_core.chains import LLMChain

# from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# llm = Ollama(model="gemma:2b", temperature=0.1)

from utility.llm_factory import LLMFactory
llm = LLMFactory.get_llm(provider="ollama", model_name="gemma:2b", temperature=0.1)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", "{question}"),
    ]
)
chain = prompt | llm | StrOutputParser()
# question = "What is the capital of France?"
# response = chain.invoke({"question": question})
# print(f"Question: {question}")
# print(f"Response: {response}")

## using steamlit UI framework
import streamlit as st
st.title("Ollama LLM Application - Demo")
question = st.text_input("Ask a question:")
if question:
    response = chain.invoke({"question": question})
    st.write(f"Response: {response}")
# Uncomment the lines below to run the Streamlit app
# if __name__ == "__main__":
#     st.run()
# Note: The above code requires the Ollama model to be running locally.

## Run the following command to start the Streamlit app:
### streamlit run 10.ollama_app.py
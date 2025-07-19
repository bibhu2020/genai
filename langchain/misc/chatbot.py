from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.utility.llm_factory2 import LLMFactory

parser = StrOutputParser()
llm = LLMFactory.get_llm("azure")

chain = llm | parser

# Here you are building a message history array and feeding to llm so that it can answer to your last question.
# You are doing this because llm does not have any concept of state. It's stateless.
result = chain.invoke(
    [
        HumanMessage(content="Hi! I'm Bob"),
        AIMessage(content="Hello Bob! How can I assist you today?"),
        HumanMessage(content="What's my name?"),
    ]
)

print(result)


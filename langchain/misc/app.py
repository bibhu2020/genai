#### Demo of a simple LLM call and a LLM call using Prompt Templates

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.utility.llm_factory2 import LLMFactory

parser = StrOutputParser()
llm = LLMFactory.get_llm("azure")


### A Simple LLM call
messages = [
    SystemMessage(content="Translate the following from English into Italian"),
    HumanMessage(content="hi!"),
]

# result = llm.invoke(messages)
# result = parser.invoke(result)
# print(result)

chain = llm | parser
result = chain.invoke(messages)
result = parser.invoke(result)
print(result)

### A LLM call using Prompt Templates
from langchain_core.prompts import ChatPromptTemplate

# A string that formats the system message
system_template = "Translate the following into {language}:"

# A string that formats the user message
user_template = "{text}"

# Lets create a prompt template combining the system and user message
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", user_template)]
)

# # Creates prompt template disctionary
# result = prompt_template.invoke({"language": "italian", "text": "hi"})
# print(result);

chain = prompt_template | llm | parser
result = chain.invoke({"language": "italian", "text": "hi!"})
result = parser.invoke(result)
print(result)


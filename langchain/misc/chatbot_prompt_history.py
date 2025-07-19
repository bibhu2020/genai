### Create a Chatbot with In-memory History of the convesation
### Demo the chat history with prompt templates

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.utility.llm_factory2 import LLMFactory

from langchain_core.chat_history import (
    BaseChatMessageHistory, # Is an abstract base class that defines how chat message history should be stored and accessed.
    InMemoryChatMessageHistory, # Is a concrete implementation of BaseChatMessageHistory that stores the chat messages in memory.
)
from langchain_core.runnables.history import RunnableWithMessageHistory # It integrates the message history into the functionality of the LLM.

parser = StrOutputParser()
llm = LLMFactory.get_llm("azure")


# Setup a chat in-memory session, and returns the base type.
store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Define a prompt template with a message placeholder / paramter called "messages"
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

chain = prompt | llm

# Tie the chat history with chain, and input message parameter.
with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="messages",
)

config = {"configurable": {"session_id": "session1"}}

# Chat#1
response = with_message_history.invoke(
    {"messages": [HumanMessage(content="hi! I'm Bibhu")], "language": "Odia"},
    config=config,
)

print(response.content)

# Chat#2 - It remembers the name of the user from the previous chat.
response = with_message_history.invoke(
    {"messages": [HumanMessage(content="What's my name?")], "language": "Odia"},
    config=config,
)

print(response.content)
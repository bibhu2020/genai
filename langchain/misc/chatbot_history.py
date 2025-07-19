### Create a Chatbot with In-memory History of the convesation

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

# Tie the chat history with llm.
with_message_history = RunnableWithMessageHistory(llm, get_session_history) 


####Let's set the session with a session_id and start the conversation.
config = {"configurable": {"session_id": "xyz"}}

# Chat#1
response = with_message_history.invoke(
    [HumanMessage(content="Hi! I'm Bob")],
    config=config,
)

print(response.content)

# Chat#2 - It remembers the name of the user from the previous chat.
response = with_message_history.invoke(
    [HumanMessage(content="What's my name?")],
    config=config,
)

print(response.content)

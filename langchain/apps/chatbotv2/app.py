from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..','..'))
from langchain.utility.llm_factory import LLMFactory
from langchain_core.output_parsers import StrOutputParser

# Initialize LangChain model and memory
def setup_langchain():
    # Create a memory object to store conversation history
    memory = ConversationBufferMemory(memory_key="history", return_messages=True)

    # Use OpenAI's GPT model
    # model = ChatOpenAI(model="gpt-3.5-turbo")  # You can use other models like GPT-4 too
    model = LLMFactory.get_llm("openai")

    # Create the conversation chain
    conversation = ConversationChain(
        llm=model,
        memory=memory,
        verbose=True
    )

    return conversation

# Initialize LangChain
conversation = setup_langchain()

def store_message(user_message, bot_message):
    conn = sqlite3.connect('/home/azureuser/projects/srescripts/pocs/genai/_data/chat_history.db')
    c = conn.cursor()
    
    # Insert user and bot messages into the history table
    c.execute('''
        INSERT INTO history (user_message, bot_message)
        VALUES (?, ?)
    ''', (user_message, bot_message))

    conn.commit()
    conn.close()

def chat_with_bot(user_input):
    # Get bot's response using LangChain conversation
    bot_response = conversation.predict(input=user_input)

    # Store the user and bot messages in the history
    store_message(user_input, bot_response)
    
    return bot_response


from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Define the request model
class ChatRequest(BaseModel):
    message: str

# Initialize FastAPI app
app = FastAPI()

@app.post("/chat/")
async def chat(request: ChatRequest):
    user_message = request.message
    bot_response = chat_with_bot(user_message)
    return {"response": bot_response}

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

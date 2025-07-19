### RAG (Retrieval Augumented Generation)
#### It helps Gen AI to answer queries that requires information from your organization document or database

import os
from openai import AzureOpenAI 
from dotenv import load_dotenv 

load_dotenv()

client = AzureOpenAI(  
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),  
    azure_endpoint=os.getenv("AZURE_OPENAI_API_URI")  
)  

deployment_name = "text-embedding-3-small" #os.getenv("AZURE_OPENAI_API_BASE_MODEL")

data="a lot of festivals are coming"

# Create embeddings / vectorize using LLM
response = client.embeddings.create(
    input = data,
    model= deployment_name
)

print(response.model_dump_json(indent=2))

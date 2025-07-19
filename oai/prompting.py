import os  
from openai import AzureOpenAI 
from dotenv import load_dotenv 

load_dotenv()

#print(os.getenv("AZURE_OPENAI_API_KEY"))
    
client = AzureOpenAI(  
     api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
     api_version=os.getenv("AZURE_OPENAI_API_VERSION"),  
     azure_endpoint=os.getenv("AZURE_OPENAI_API_URI")  
)  

# This will correspond to the custom name you chose for your deployment when you deployed a model.  
# Use a gpt-35-turbo-instruct deployment.  
deployment_name = os.getenv("AZURE_OPENAI_API_BASE_MODEL") 

# Send a completion call to generate an answer  
messages = [
     {"role": "system", "content": "You are a helpful assistant."},
     {"role": "user", "content": "List out all the players in the indian national cricket team for ODI."}
]  

# Chat is used for multi-turn convesations where assistant maintains context across multiple interactions.
response = client.chat.completions.create(
    model="gpt-4o-mini", 
    temperature=0.2,
    messages=messages)
print(response.choices[0].message.content)

# Completion is intended for single-turn tasks and is used for use cases such as summarization, content generation, and classification.
response = client.completions.create(  
      model=deployment_name,  
      prompt="List out all the players in the indian national cricket team.",  
      temperature=1,  
      max_tokens=100,  
      top_p=0.5,  
      frequency_penalty=0,  
      presence_penalty=0,  
      best_of=1,  
      stop=None  
)

print(response.choices[0].text)

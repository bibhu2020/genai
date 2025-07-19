#### Demonstrate RAG (using predefined Azure AI Search MODEL)
# It stores the pdf documents in Azure Blob. Azure AI Search Service crawls and indexes them.
# You then use Azure Search AI to retrieve the content which you feed to openai for analyzing.

import os
from openai import AzureOpenAI 
from dotenv import load_dotenv 
#from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

load_dotenv()
index_name="trainingdata-index"
endpoint=os.getenv("AZURE_AI_SEARCH_ENDPOINT")
key=os.getenv("AZURE_AI_SEARCH_KEY")

client = AzureOpenAI(  
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),  
    azure_endpoint=os.getenv("AZURE_OPENAI_API_URI")  
)  

deployment_name = os.getenv("AZURE_OPENAI_API_BASE_MODEL") 

#setting important variables
max=0
lst=[]
sum=""

#create an azure search client
# print(key)
# print(endpoint)
# credential=AzureKeyCredential(key)
credential = DefaultAzureCredential()
search_client=SearchClient(endpoint=endpoint,index_name=index_name,credential=credential)

results=search_client.search(search_text="jee advanced 2023")

for result in results:
    if result['@search.score']>max:
        max=result['@search.score']
        lst=result['keyphrases']

for keyphrases in lst:
    sum = sum + keyphrases + " "

prompt = "You are an AI assistant, you are given a set of keyphrases extracted from the pdf file of an engineering entrance examination's question paper. By making a note of all these keyphrases, list down all the important engineering topics such as fluid dynamics, thermo dynamics, etc..."

messages = [
    {"role":"system", "content": prompt},
    {"role":"user", "content": sum},
]

response = client.chat.completions.create(
    model="gpt-4",
    messages=messages
)

print(response.choices[0].message.content)

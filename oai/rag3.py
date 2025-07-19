import os
import requests
import json
from openai import AzureOpenAI 
from dotenv import load_dotenv 
from azure.identity import DefaultAzureCredential

load_dotenv()

service_endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")

client = AzureOpenAI(  
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),  
    azure_endpoint=os.getenv("AZURE_OPENAI_API_URI")  
)  

# Get DefaultAzureCredential (this will use environment variables, managed identity, or interactive login)
credential = DefaultAzureCredential()

# Get the access token
#token = credential.get_token("https://cognitiveservices.azure.com/.default")
token = credential.get_token("https://search.azure.com/.default")
access_token = token.token

headers={
    "Authorization": f"Bearer {access_token}",
    'Content-Type': 'application/pdf'  # Make sure to set the correct content type for PDF
}
headers2={
    "Authorization": f"Bearer {access_token}",
    'Content-Type': 'application/json'
}

embedding_engine_model = "text-embedding-3-small" 
chat_enginee_model = "gpt-4"

index_name = "vector-index"

#Step1: Store the documents in Azure Storage Blob

#Step2: From Azure Search AI, vecotorize the content and create index. (overview >> import and vectorize data)
# this is done from azure portal, not from the program here.

#Step3: Create embeddings from the user query
def generate_embeddings(client, text):
    embedding_model = embedding_engine_model
    
    response = client.embeddings.create(
        input=text,
        model = embedding_model
    )
    
    embeddings=response.model_dump()
    return embeddings['data'][0]['embedding']

#Step4: Make Azure AI Search API call to find the matching vectorized contents.
def find_the_matches(vectorised_user_query):
    context=[]

    try:
        url = f"{service_endpoint}/indexes/{index_name}/docs/search?api-version=2023-11-01"

        # print(url)
        #print(headers2)
            
        body =   {
                "count": True,
                "select": "chunk",
                "vectorQueries": [
                    {
                        "vector": vectorised_user_query,
                        "k": 3,
                        "fields": "text_vector",
                        "kind": "vector"
                    }
                ]
            }
            
        response = requests.post(url, headers=headers2, data=json.dumps(body))
        
        # # Check if the status code indicates success
        # if response.status_code == 200:
        #     print("Request succeeded!")
        #     print("Response content:", response.json())  # If the response is JSON
        # else:
        #     print(f"Request failed with status code {response.status_code}")
        #     print("Error details:", response.text)  # For debugging


        documents = response.json()['value']

        for doc in documents:
            context.append(dict(
                {
                    "chunk": doc['chunk'],
                    "score": doc['@search.score']
                    
                }
            ))

        return context
            
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)    

# Step5: Send the prompt/user query to GPT for answer
def query_gpt(context, user_query):
    system_prompt = f"""
    
    You are meant to behave as a RAG chatbot that derives its context from a database of hotel reviews stored in Azure AI Search Solution.
    please answer strictly from the context from the database provided and if you dont have an answer please politely say so. dont include any extra 
    information that is not in the context and dont include links as well.
    the context passed to you will be in the form of a pythonic list with each object in the list containing details of hotel reviews and
    having structure as follows:

    "chunk": "the content of the review",
    "score": "the relevancy score of the review"


    the pythonic list contains best 2 matches to the user query based on cosine similarity of the embeddings of the user query and the review descriptions.
    please structure your answers in a very professional markdown format and in such a way that the user does not get to know that its RAG working under the hood
    and its as if they are talking to a human. 
    
    """

    # here you create prompt combining the user query and the retrieved contents from vector db
    user_prompt = f""" the user query is: {user_query}
                       the context is : {context}"""

    chat_completions_response = client.chat.completions.create(
        model = chat_enginee_model,
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )

    print(chat_completions_response.choices[0].message.content)

if __name__ == "__main__":
    context=[]
    user_query = "What is the review of the creek hotel in Dubai?"
    vectorised_user_query = generate_embeddings(client, user_query)
    context = find_the_matches(vectorised_user_query)
    # for doc in context:
    #         print(doc)
    query_gpt(context, user_query)


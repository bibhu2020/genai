### Reading Handwritings using Azure Open AI
### It uses gpt-4o to process the handwritten images and reads out the text for you.

import os
from openai import AzureOpenAI
import asyncio
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),  
    azure_endpoint=os.getenv("AZURE_OPENAI_API_URI")
)

file_path = "https://abadguide.wordpress.com/wp-content/uploads/2012/01/jh66.jpg" #"https://genaipoc2024stg.blob.core.windows.net/trainingdataset/handwritten.jpg"

async def describe_image():
        url = file_path #input("Enter the URL of the image: ")
        print("Processing...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role":"user",
                    "content":[
                        {"type":"text", "text":"what's in this image?"},
                        {"type":"image_url",
                         "image_url": 
                            {
                             "url": url
                            }
                        }
                    ]
                }
            ]
        )
        os.system('clear')
        print(response.choices[0].message.content)
    
asyncio.run(describe_image())
        
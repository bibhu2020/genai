### Function call
# Calls Weather service to get you real-time data

import json
import os  
from openai import AzureOpenAI 
from dotenv import load_dotenv 
import requests

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

functions=[
    {
        "name": "get_weather",
        "description": "Retrieves weather data for a specified location.",
        "parameters": {
            "type": "object",
            "properties": {
            "location": {
                "type": "string",
                "description": "The name of the location for which to retrieve weather data."
            }
            },
            "required": ["location"]
        }
    }
  ]



# Replace this with your actual OpenWeather API key
WEATHER_SERVICE_API_KEY = os.getenv("WEATHER_SERVICE_API_KEY") 
print(WEATHER_SERVICE_API_KEY)

def get_weather(location):
    weather_api_url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_SERVICE_API_KEY}&units=metric'
    
    try:
        # Sending the GET request to the weather API
        response = requests.get(weather_api_url)
        
        # Checking if the response is valid
        data = response.json()
        
        # If the API response has a cod (status) other than 200, it indicates an error
        if data.get('cod') != 200:
            print(f"Error reading weather data for {location}: {data.get('message')}")
            return None
        
        # Extract relevant weather data
        weather_info = {
            'city': data.get('name'),
            'temperature': data.get('main', {}).get('temp'),
            'description': data.get('weather', [{}])[0].get('description'),
            'humidity': data.get('main', {}).get('humidity'),
            'windSpeed': data.get('wind', {}).get('speed')
        }

        # Printing the weather information
        print(weather_info)
        
        # Returning the weather information
        return weather_info

    except requests.exceptions.RequestException as error:
        # Handling errors related to the request, e.g., network issues
        print(f"Error reading weather: {str(error)}")
        return None



# Send a completion call to generate an answer  
messages = [
     {"role": "system", "content": "You are an assistant who helps retrieve real-time weather data/info."},
     {"role": "user", "content": "How is weather in 'South Padre Island'?."}
]  

# Chat is used for multi-turn convesations where assistant maintains context across multiple interactions.
initial_response = client.chat.completions.create(
    model="gpt-4o-mini", 
    messages=messages,
    functions=functions)

# Extract the function call from the model's response
function_call = initial_response.choices[0].message.function_call

# Check if the response includes a function call (to get weather data)
if function_call:
    function_name = function_call.name
    function_arguments = json.loads(function_call.arguments)

    # Automatically call the relevant function based on the parsed name and arguments
    if function_name == "get_weather":
        location = function_arguments.get("location")
        
        # Call the weather function with the extracted location
        if location:
            print(f"Location extracted: {location}")
            
            # Call the weather function with the extracted location
            weather_data = get_weather(location)
            
            # If weather data was successfully retrieved, send it back as part of the response
            if weather_data:
                # Simulate what would happen if OpenAI needed to continue the conversation
                final_response = {
                    "status": "success",
                    "data": weather_data
                }
                
                print("Weather Data:", final_response)
            else:
                print("Failed to retrieve weather data.")
        else:
            print("No location found in function call.")
    else:
        print("No valid function call found in the response.")
else:
    print("No function call found in the OpenAI response.")

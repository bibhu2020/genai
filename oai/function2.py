### Multi-Function call
# Calls Weather & yahoo finance service to get you real-time weather report and stock value

import json
import os
from openai import AzureOpenAI 
from dotenv import load_dotenv 
import requests
import yfinance as yf  # Import yfinance to fetch stock data

load_dotenv()

client = AzureOpenAI(  
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),  
    azure_endpoint=os.getenv("AZURE_OPENAI_API_URI")  
)  

deployment_name = os.getenv("AZURE_OPENAI_API_BASE_MODEL") 

functions = [
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
    },
    {
        "name": "get_stock_data",
        "description": "Retrieves real-time stock data for a specified stock symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock symbol (ticker) for which to retrieve data."
                }
            },
            "required": ["symbol"]
        }
    }
]

# Function to get weather data
WEATHER_SERVICE_API_KEY = os.getenv("WEATHER_SERVICE_API_KEY") 

def get_weather(location):
    weather_api_url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_SERVICE_API_KEY}&units=metric'
    
    try:
        response = requests.get(weather_api_url)
        data = response.json()

        if data.get('cod') != 200:
            print(f"Error reading weather data for {location}: {data.get('message')}")
            return None
        
        weather_info = {
            'city': data.get('name'),
            'temperature': data.get('main', {}).get('temp'),
            'description': data.get('weather', [{}])[0].get('description'),
            'humidity': data.get('main', {}).get('humidity'),
            'windSpeed': data.get('wind', {}).get('speed')
        }

        print(weather_info)
        return weather_info

    except requests.exceptions.RequestException as error:
        print(f"Error reading weather: {str(error)}")
        return None

# Function to get stock data
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    stock_info = stock.history(period="1d")

    if stock_info.empty:
        print(f"Error: No data found for {symbol}")
        return None

    stock_data = {
        "symbol": symbol,
        "open": stock_info["Open"].iloc[0],
        "close": stock_info["Close"].iloc[0],
        "high": stock_info["High"].iloc[0],
        "low": stock_info["Low"].iloc[0],
        "volume": stock_info["Volume"].iloc[0],
    }

    print(stock_data)
    return stock_data

# Send a completion call to generate an answer  
messages = [
    {"role": "system", "content": "You are an assistant who helps retrieve real-time weather or stock data."},
    {"role": "user", "content": "What's the stock data for AAPL?"}  # Modify this line for testing different queries
]

# messages = [
#      {"role": "system", "content": "You are an assistant who helps retrieve real-time weather data/info."},
#      {"role": "user", "content": "How is weather in 'South Padre Island'?."}
# ]  


# Chat is used for multi-turn conversations where assistant maintains context across multiple interactions.
initial_response = client.chat.completions.create(
    model="gpt-4",  # Use the correct model name
    messages=messages,
    functions=functions,
    function_call="auto"  # This allows the model to call the function automatically
)

# Extract the function call from the model's response
function_call = initial_response.choices[0].message.function_call

# Check if the response includes a function call (to get weather or stock data)
if function_call:
    function_name = function_call.name
    function_arguments = json.loads(function_call.arguments)

    # Automatically call the relevant function based on the parsed name and arguments
    if function_name == "get_weather":
        location = function_arguments.get("location")
        
        if location:
            print(f"Location extracted: {location}")
            weather_data = get_weather(location)
            
            if weather_data:
                final_response = {
                    "status": "success",
                    "data": weather_data
                }
                print("Weather Data:", final_response)
            else:
                print("Failed to retrieve weather data.")
        else:
            print("No location found in function call.")
    
    elif function_name == "get_stock_data":
        symbol = function_arguments.get("symbol")
        
        if symbol:
            print(f"Stock symbol extracted: {symbol}")
            stock_data = get_stock_data(symbol)
            
            if stock_data:
                final_response = {
                    "status": "success",
                    "data": stock_data
                }
                print("Stock Data:", final_response)
            else:
                print("Failed to retrieve stock data.")
        else:
            print("No stock symbol found in function call.")
    
    else:
        print("No valid function call found in the response.")
else:
    print("No function call found in the OpenAI response.")
    
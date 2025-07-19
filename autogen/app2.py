## Demo a 2 agent chart reading weather and stock data
## It uses custom tools/functions to get the real-time weather and stock data

import os
import autogen
import logging
import numpy as np
from pydantic import BaseModel, Field
from typing import Annotated
from dotenv import load_dotenv 
import requests
import yfinance as yf  # Import yfinance to fetch stock data
from utility.llm_config import LLMConfig

# Setup logging
logging.basicConfig(level=logging.INFO)

llm_manager = LLMConfig(
    seed=42,
    temperature=0,
    is_azure_open_ai=False,
    model_name="gpt-4"
)
# Get the configuration for autogen
llm_config = llm_manager.llm_config

# Let's first define the assistant agent that suggests tool calls.
weather_assistant = autogen.AssistantAgent(
    name="Weather_Assistant",
    system_message="You are a helpful AI assistant. "
    "You can help with realtime weather data. "
    "Return 'TERMINATE' when the task is done.",
    llm_config=llm_config,
)

stock_assistant = autogen.AssistantAgent(
    name="Stock_Assistant",
    system_message="You are a helpful AI assistant. "
    "You can help with realtime stock data. "
    "Return 'TERMINATE' when the task is done.",
    llm_config=llm_config,
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
)

## Define Custom Tools
class WeatherInput(BaseModel):
    location: Annotated[str, Field(description="Location Name.")]

class StockInput(BaseModel):
    ticker: Annotated[str, Field(description="Stock Name.")]
    
def get_weather(input: Annotated[WeatherInput, "Extra Weather Data."]) -> str:
    # Function to get weather data
    WEATHER_SERVICE_API_KEY = os.getenv("WEATHER_SERVICE_API_KEY") 
    weather_api_url = f'https://api.openweathermap.org/data/2.5/weather?q={input.location}&appid={WEATHER_SERVICE_API_KEY}&units=metric'
    
    try:
        response = requests.get(weather_api_url)
        data = response.json()

        if data.get('cod') != 200:
            print(f"Error reading weather data for {input.location}: {data.get('message')}")
            return None
        
        weather_info = {
            'city': data.get('name'),
            'temperature': data.get('main', {}).get('temp'),
            'description': data.get('weather', [{}])[0].get('description'),
            'humidity': data.get('main', {}).get('humidity'),
            'windSpeed': data.get('wind', {}).get('speed')
        }

        return weather_info

    except requests.exceptions.RequestException as error:
        print(f"Error reading weather: {str(error)}")
        return None
    
# Function to get stock data
def get_stock_data(input: Annotated[StockInput, "Extra Weather Data."]) -> str:
    stock = yf.Ticker(input.ticker)
    stock_info = stock.history(period="1d")

    if stock_info.empty:
        print(f"Error: No data found for {input.ticker}")
        return None

    stock_data = {
        "symbol": input.ticker,
        "open": int(stock_info["Open"].iloc[0]),
        "close": int(stock_info["Close"].iloc[0]),
        "high": int(stock_info["High"].iloc[0]),
        "low": int(stock_info["Low"].iloc[0]),
        "volume": int(stock_info["Volume"].iloc[0]),
    }

    return stock_data

# Register the tools with the assistants
weather_assistant.register_for_llm(name="get_weather", description="A get_weather tool that accepts nested expression as input")(get_weather)
stock_assistant.register_for_llm(name="get_stock_data", description="A get_stock_data tool that accepts nested expression as input")(get_stock_data)
user_proxy.register_for_execution(name="get_weather")(get_weather)
user_proxy.register_for_execution(name="get_stock_data")(get_stock_data)

# Define task
task = f"""
Read me today's weather in Bhubaneswar.
After showing me the weather, please get me the TESLA stock price in MD format also.
"""

class TaskHandler:
    def __init__(self, task):
        self.task = task

    def run(self, user_proxy, assistant):
        user_proxy.initiate_chat(assistant, message=self.task)

try:
    # Initiate chat
    logging.info("Initiating chat...")
    # Initialize task handler and run the task
    task_handler = TaskHandler("Read me today's weather in JSON format for Bhubaneswar, Dallas, Melissa, and Balasore.")
    task_handler.run(user_proxy, weather_assistant)

    task_handler = TaskHandler("Please get me the TESLA & APPLE stock price in one JSON file format.")
    task_handler.run(user_proxy, stock_assistant)
except Exception as e:
    logging.error(f"An error occurred: {e}")

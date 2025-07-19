## This is a demo program to summerize youtube video
import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

#print(os.getenv("CHATGPT_MODEL"))

from IPython.display import YouTubeVideo
from pytubefix import YouTube

from openai import AzureOpenAI
import json
import evaluate
import re
import tiktoken

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from datasets import load_dataset
from collections import Counter
from tqdm import tqdm
import textwrap
import yt_dlp
import whisper

## define llm client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_APIVERSION")
)

deployment_name = os.getenv("CHATGPT_MODEL")

audio_path="/mnt/c/Users/msuni/genai/gl/week10/temp.mp3"

#################################################################################################################
############################# DOWNLOAD THE YOUTUBE VIDEO TO LOCAL DRIVE
def download_youtube_video():
    # Link to the youtube video
    video_link = "https://www.youtube.com/watch?v=8l8fpR7xMEQ"

    # destination path
    destination = '/mnt/c/Users/msuni/genai/gl/week10/'

    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(destination, 'temp.%(ext)s'),
        'quiet': True
    }

        # 'outtmpl': os.path.join(destination, '%(title)s.%(ext)s'),

    # Download the audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_link, download=True)
        title = info['title']

        # Get the actual file path
        new_file = ydl.prepare_filename(info)
        # Since we're converting to mp3, replace the extension
        new_file = new_file.rsplit(".", 1)[0] + ".mp3"
        #new_file = "temp.mp3"

        print(f"{title} has been successfully downloaded.")
        print(f"File saved as: {new_file}")


def generate_script_from_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcript = result["text"]
    print(textwrap.fill(transcript,width = 150))


def summarize(transcript, system_message):
  response = ""
  message = [
      {"role": "system", "content": system_message},
      {"role": "user", "content": transcript}
  ]
  try:
    # Get the chat completion
    response = client.chat.completions.create(
        model=deployment_name,
        messages=message,
        temperature = 0
    )
    # print(response.choices[0].message.content) # uncomment to check the response of the LLM individually for each transcript.
    response = response.choices[0].message.content

  except Exception as e:
    print(e) # A better error handling mechanism could be implemented

  return response


if __name__ == "__main__":
    #download_youtube_video()

    zero_shot_system_message = """You are helpful assistant. Summarize the following youtube transcript in  5-10 lines.
        Keep it concise and make sure to include all the important points. Do mention all the topics covered in the transcript shared
        """
    transcript = generate_script_from_audio(audio_path)
    summary_response = summarize(transcript, zero_shot_system_message)
    print(textwrap.fill(summary_response,width = 150))


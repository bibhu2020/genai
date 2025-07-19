############## PROBLEM STATEMENT
### Summarize a long YouTube Video

############## PROBLEM SOLVING APPROACH

# Import necessary libraries
import os
import sys
import yt_dlp
import whisper

# Add utility module path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..'))
from langchain.utility.llm_factory2 import LLMFactory

# Define YouTubeTranscripter class
class YouTubeTranscripter:
    destination = '/mnt/c/Users/v-bimishra/workspace/srescripts/pocs/genai/_data/'

    # Download the audio of the video from YouTube
    @staticmethod
    def __download_video(url):
        audio_path = YouTubeTranscripter.destination + "temp.mp3"

        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(YouTubeTranscripter.destination, 'temp.%(ext)s'),
            'quiet': True
        }

        # Check if audio file exists, if not download it
        if os.path.exists(audio_path):
            print(f"{audio_path} exists. No more downloads.")
        else:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info['title']
                new_file = ydl.prepare_filename(info)
                new_file = new_file.rsplit(".", 1)[0] + ".mp3"
                print(f"{title} has been successfully downloaded.")
                print(f"File saved as: {new_file}")

        return audio_path

    # Generate transcript from the downloaded audio
    @staticmethod
    def __generate_scripts_from_audio(audio_path):
        script_file = YouTubeTranscripter.destination + "temp.txt"
        transcript = ""

        # Check if transcript already exists, if not, generate it
        if os.path.exists(script_file):
            print(f"{script_file} exists. No need to generate again.")
            with open(script_file, "r") as file:
                transcript = file.read()
        else:
            model = whisper.load_model("base")
            result = model.transcribe(audio_path)
            transcript = result["text"]

            # Save the generated transcript
            with open(script_file, "w") as file:
                file.write(transcript)

        return transcript

    # Rate the generated summary based on accuracy
    @staticmethod
    def rate_the_summary(summary_response, transcripts):
        rater_system_message = """
            You are tasked with rating AI-generated summaries of youtube transcripts based on the given metric.
            You will be presented a transcript and an AI-generated summary of the transcript as input.
            The transcript will begin with ###transcript and the AI-generated summary with ###summary.
            Metric: Check if the summary is true to the transcript and covers all major points concisely.
            Evaluation criteria:
            Rate the extent to which the metric is followed on a scale from 0 to 5.
        """

        rater_user_message_template = """
            ###transcript
            {transcript}

            ###summary
            {summary}
        """

        client = LLMFactory.get_llm("openai")
        
        from langchain_core.output_parsers import StrOutputParser
        parser = StrOutputParser()

        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate([("system", rater_system_message),
                                    ("human", rater_user_message_template.format(transcript=transcripts, summary=summary_response))])

        chain = prompt | client | parser

        response = chain.invoke({"transcript": transcripts, "summary": summary_response},
                config={"temperature": 0, "max_tokens": 5, "model_name": "gpt-4o"})
        
        return response

    # Summarize the YouTube video by downloading and transcribing
    @staticmethod
    def summarize(video_link, system_message):
        audio_path = YouTubeTranscripter.__download_video(video_link)
        transcripts = YouTubeTranscripter.__generate_scripts_from_audio(audio_path)

        summary_response = ""
        message = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": transcripts}
        ]
        try:
            # Get the chat completion
            client = LLMFactory.get_llm("openai")
            
            from langchain_core.output_parsers import StrOutputParser
            parser = StrOutputParser()

            chain = client | parser

            summary_response = chain.invoke(message,
                    config={"temperature": 0, "max_tokens": 500, "model_name": "gpt-4o-mini"})

        except Exception as e:
            print(f"Error: {e}")  # A better error handling mechanism could be implemented

        return summary_response, transcripts

# Main script to run the summarization
if __name__ == "__main__":
    # Define YouTube video link
    video_link = "https://www.youtube.com/watch?v=8l8fpR7xMEQ"
    
    # Define system message for zero-shot prompting
    zero_shot_system_message = """You are helpful assistant. Summarize the following youtube transcript in 5-10 lines.
        Keep it concise and include all important points. Mention all the topics covered in the transcript."""
    
    # Get summary and transcripts for the video
    summary_response, transcripts = YouTubeTranscripter.summarize(video_link, zero_shot_system_message)
    
    # Print the summary result
    print(f"YouTube Video: {video_link}")
    print("=================================================================================")
    print(f"Summarization using zero-shot-prompting:\n{summary_response}")

    # Evaluate the summary using the defined rating mechanism
    summary_rating = YouTubeTranscripter.rate_the_summary(summary_response, transcripts)
    print("---------------------------------------------------------------------------------")
    print(f"Rating of the summarization: {summary_rating}")

    # Define system message for chain-of-thought (CoT) prompting
    cot_system_message = """
        You are a helpful assistant that summarizes YouTube transcripts.
        Think step-by-step, focus on the main ideas, and summarize in clear and concise language.
        Ensure the summary is coherent, includes essential details, and reflects the original meaning.
    """
    
    # Get summary and transcripts for the CoT approach
    summary_response, transcripts = YouTubeTranscripter.summarize(video_link, cot_system_message)
    
    # Print the summary result for CoT approach
    print(f"YouTube Video: {video_link}")
    print("=================================================================================")
    print(f"Summarization using chain-of-thought prompting:\n{summary_response}")

    # Evaluate the summary generated by the CoT method
    summary_rating = YouTubeTranscripter.rate_the_summary(summary_response, transcripts)
    print("---------------------------------------------------------------------------------")
    print(f"Rating of the summarization: {summary_rating}")

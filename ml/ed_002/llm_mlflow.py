import os
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.callbacks.mlflow_callback import MLflowCallbackHandler

import mlflow

# Load your OpenAI API key
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Set MLflow tracking URI and experiment
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("Q&A Tracing")

# Initialize MLflow callback handler
mlflow_callback = MLflowCallbackHandler()

# Set up LLM
llm = OpenAI(temperature=0.7, max_tokens=1000)

# Prompt template
question_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
    You are a helpful chat agent. You answer questions based on provided context only. 
    Context: {context}
    Question: {question}
    Answer:
    """,
)

# Chain prompt → LLM
chain = question_prompt | llm

# Start MLflow run manually (optional but useful for grouping)
with mlflow.start_run():
    response = chain.invoke(
        {
            "context": """The Taj Mahal is an ivory-white marble mausoleum on the right bank of the river Yamuna in Agra, Uttar Pradesh, India. 
            It was commissioned in 1631 by Shah Jahan to house the tomb of his wife, Mumtaz Mahal.""",
            "question": "Where is Taj Mahal situated?",
        },
        config={"callbacks": [mlflow_callback]},  # ✅ Callback to log run
    )

    print("Response:\n", response)

import os
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agents.agentic_workflow import GraphBuilder
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pydantic import BaseModel, root_validator, validator
import pandas as pd
from langchain_core.messages import HumanMessage 

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request model with validation
class QueryRequest(BaseModel):
    appName: str
    burnRate: float
    incidentTime: datetime  # ✅ FIXED
    severity: str
    bNotify: bool

    # @validator('burnRate')
    # def validate_burn_rate(cls, value):
    #     allowed_burn_rates = ['low', 'medium', 'high']
    #     if value not in allowed_burn_rates:
    #         raise ValueError('Invalid burn rate, must be one of: low, medium, high')
    #     return value

    @validator('severity')
    def validate_severity(cls, value):
        allowed_severities = ['sev1', 'sev2', 'sev3', 'sev4']
        if value not in allowed_severities:
            raise ValueError('Invalid severity, must be one of: sev1, sev2, sev3, sev4')
        return value

@app.get("/healthz")
async def healthz():
    """
    Health check endpoint to verify if the service is running.
    """
    return {"status": "ok"}

# Define the endpoint to analyze burn rate
@app.post("/analyze-burnrate")
async def analyze_incident_burnrate(query: QueryRequest):
    try:
        # Log the incoming request data for debugging
        logger.info(f"Received request: {query.dict()}")

        # Initialize the GraphBuilder instance
        graph = GraphBuilder(model_provider="groq")
        react_agent = graph()  # Calls the __call__() method in the class

        # Generate the graph and save it as PNG
        png_graph = react_agent.get_graph().draw_mermaid_png()
        with open("my_graph.png", "wb") as f:
            f.write(png_graph)

        logger.info(f"Graph saved as 'my_graph.png' in {os.getcwd()}")
        
        # Prepare the message to send to the LLM
        print(f"Incident time: {query.incidentTime}")
        message = f""" 
            A spike in error burn rate was detected for the application {query.appName} at around time {query.incidentTime.strftime('%Y-%m-%d %H:%M:%S')}.
            Analyze the root cause of the incident, notify the SRE team about severity {query.severity}.
            Also recommend how to mitigate or restore the application from the incident.
        """
        
        messages = {"messages": [HumanMessage(content=message)], "appName": query.appName, "incidentTime": query.incidentTime.strftime('%Y-%m-%d %H:%M:%S'),
                    "severity": query.severity, "sendNotification": bool}

        output = react_agent.invoke(messages)

        # Process the response from the LLM
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content  # Last AI response
        else:
            final_output = str(output)
        
        return {"answer": final_output}

    except Exception as e:
        # Log the error and return a 500 error response
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})


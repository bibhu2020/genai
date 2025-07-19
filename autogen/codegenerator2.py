### Demo a 2 agent chart summerizing a blog article

import logging
from utility.llm_config import LLMConfig

# Setup logging
logging.basicConfig(level=logging.INFO)

llm_manager = LLMConfig(
    seed=42,
    temperature=0,
    is_azure_open_ai=True,
    model_name="gpt-4"
)

# Get the configuration for autogen
llm_config = llm_manager.llm_config

import tempfile
from autogen import ConversableAgent
from autogen.coding import DockerCommandLineCodeExecutor, LocalCommandLineCodeExecutor

# Create a temporary directory to store the code files.
temp_dir = tempfile.TemporaryDirectory()

# Create a Docker command line code executor.
executor = DockerCommandLineCodeExecutor(
    image="python:3.12-slim",  # Execute code using the given docker image name.
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir=temp_dir.name,  # Use the temporary directory to store the code files.
)

# Create a local command line code executor.
executor2 = LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir= "./code" #temp_dir.name,  # Use the temporary directory to store the code files.
)


# Create an agent with code executor configuration that uses docker.
code_executor_agent_using_docker = ConversableAgent(
    "code_executor_agent_docker",
    llm_config=False,  # Turn off LLM for this agent.
    code_execution_config={"executor": executor2},  # Use the docker command line code executor.
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",  # Always take human input for this agent for safety.
)

# The code writer agent's system message is to instruct the LLM on how to use
# the code executor in the code executor agent.
code_writer_system_message = """
You are a helpful AI assistant.
Solve tasks using your coding and language skills.
In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.
1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
Reply 'TERMINATE' in the end when everything is done.
"""

code_writer_agent = ConversableAgent(
    "code_writer_agent",
    system_message=code_writer_system_message,
    llm_config=llm_config,
    code_execution_config=False,  # Turn off code execution for this agent.
)

path = "/mnt/c/Users/v-bimishra/workspace/srescripts/pocs/genai/autogen/"

chat_result = code_executor_agent_using_docker.initiate_chat(
    code_writer_agent,
    # message="""
    # Analyze the market data and find out 3 top stocks that looks high yeilding in next 30 days.
    # In order to arrive at the right conclusion, do pull down the financial data available about the stocks in yahoo finance.
    #    - Perform fundamental and technical analysis on the data and the last 3 months trend.
    #    - Look into the recent news about the stocks, public sentiment in the market and earning reports.
    #    - Finally, help me distributing my $2000 into the 3 stocks that would earn me the most in 30 days.
    # """
    # message="""
    # Analyze the market data and find out 3 top stocks that looks high yeilding in next 30 days.
    # In order to arrive at the right conclusion, do pull down the financial data available about the stocks in yahoo finance.
    #    - Perform fundamental and technical analysis on the data and the last 3 months trend.
    #    - Look into the recent news about the stocks, political situation impact, public sentiment in the market and earning reports.
    #    - Finally, suggest me 3 options spreads with each leg detailed with strike price, premium, and expiry date.
    # """
    # message="""
    # Read the Indian media, social media and market news. Analyze the market trend from last 30 days.
    # Perform a market sentimate analysis based on inputs you collect and summerize it.
    # """

    # message="""
    # Perform load testing on my web application (https://oauthapp.azurewebsites.net/). The app is a CMS site, and I want to simulate user behavior to test how well it handles traffic. The key goals are to assess how the app performs when multiple users access it simultaneously and to measure response times, throughput, and error rates under heavy load.

    # Specifics:
    # 1. Tools: Use Locust or JMeter to create the load testing script.
    # 2. Load: Simulate traffic for up to 10 concurrent users over a 5-minutes period.
    # 3. Metrics to Track:
    #     - Response time (average, peak)
    #     - Throughput (requests per second)
    #     - Error rates (e.g., 5xx errors, timeouts)
    # 4. User Actions: Each simulated user should perform the following actions in the app:
    #     - Browse the home page
    #     - Navigate down 1 page down by clicking the links the page
    # 5. Expected Outcome: I need a detailed report on the app’s ability to handle the load, highlighting any performance bottlenecks or crashes.

    # Please include instructions on how to run the test, set up the environment, and any configuration adjustments for optimal testing.
    # """
    message=f"""
    Review the code files in folder ${path} and document the code as necessary.
    """

)



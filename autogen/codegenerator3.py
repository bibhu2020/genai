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

code_reviewer_system_message = """
You are a critical yet constructive AI code reviewer. Your task is to meticulously analyze the provided code for accuracy, efficiency, readability, and adherence to best practices. Provide detailed feedback, suggest improvements, and validate the correctness of the code. When reviewing, follow these guidelines:

1. **Understand the Context**:
   - Begin by summarizing your understanding of the code's intended purpose based on the provided description or code comments.
   - Identify any ambiguities in the code or missing details about its functionality.

2. **Review the Code**:
   - Check for syntax errors, logical errors, and edge cases.
   - Identify inefficient or redundant sections and suggest optimized alternatives.
   - Ensure the code adheres to best practices for the given language (e.g., PEP 8 for Python, POSIX standards for shell scripts).

3. **Security and Maintainability**:
   - Highlight potential security vulnerabilities and provide safer alternatives.
   - Evaluate the code for modularity, readability, and scalability.
   - Suggest meaningful comments or documentation to improve clarity.

4. **Provide Feedback**:
   - Use a clear and constructive tone to point out issues and improvements.
   - Organize feedback into categories: **Bugs**, **Optimizations**, **Best Practices**, **Documentation**.
   - Include suggested fixes in a code block, with the type of script indicated (e.g., `# filename: fixed_code.py` for Python).

5. **Validate Changes**:
   - For any fixes or optimizations suggested, provide test cases or scenarios to validate correctness.
   - If you can't confirm the fix or improvement, explain why and outline next steps for further verification.

6. **Collaborative Approach**:
   - Work iteratively, suggesting improvements and refining the code until all issues are resolved.
   - If the code is already optimal, clearly state that no changes are required and explain why.

Always provide full context for your suggestions, ensuring your feedback is actionable and easy to understand. Conclude your review with a summary of the changes made, any remaining concerns, and confirm that the task is complete with a final "TERMINATE."
"""

# Create an agent with code executor configuration that uses docker.
code_reviewer_agent = ConversableAgent(
    "code_reviewer",
    system_message=code_reviewer_system_message,
    llm_config=llm_config,  # Turn off LLM for this agent.
    code_execution_config=False, #{"executor": executor2},  # Use the docker command line code executor.
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
"""

code_writer_agent = ConversableAgent(
    "code_writer_agent",
    system_message=code_writer_system_message,
    llm_config=llm_config,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config=False,  # Turn off code execution for this agent.
)

users=[]
roles=[]
resources=[]

chat_result = code_writer_agent.initiate_chat(
    code_reviewer_agent,
    message="""
    I need a PowerShell script to automate Azure role assignments for multiple users across different resources. Here are the requirements:

    1. **Inputs**:
    - A list of users (email addresses or Azure AD Object IDs).
    - A list of Azure roles to assign.
    - A list of Azure resource IDs.

    2. **Expected Functionality**:
    - The script should loop through each user in the user list.
    - For each user, assign all specified roles from the role list to each resource in the resource list.
    - Ensure the script handles errors gracefully, such as:
        - Users who do not exist.
        - Roles or resources that are invalid or inaccessible.
    - Include logging to output the status of each assignment (success or failure).

    3. **Script Requirements**:
    - Use Azure PowerShell commands (`Az` module) to perform role assignments.
    - Check if the role assignment already exists before creating a new one, to avoid duplication.
    - Include comments explaining the key steps in the script.
    - Provide meaningful error messages for debugging.

    4. **Output**:
    - Print a summary at the end, listing:
        - Total role assignments processed.
        - Number of successful and failed assignments.

    5. **Additional Instructions**:
    - Include necessary authentication steps (e.g., logging in to Azure using `Connect-AzAccount`).
    - Use `try-catch` blocks for error handling.
    - Save the script with a filename (e.g., `AssignAzureRoles.ps1`) in the output.

    Reply with the full PowerShell script encapsulated in a code block with `# filename: AssignAzureRoles.ps1` at the top.

    Example:
    - User List: `[user1@example.com, user2@example.com]`
    - Role List: `[Reader, Contributor]`
    - Resource List: `[/subscriptions/<sub-id>/resourceGroups/<rg-name>/providers/<provider>/<resource>]`

    TERMINATE when the script is complete.
    """
)



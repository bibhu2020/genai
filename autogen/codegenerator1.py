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
from autogen.coding import LocalCommandLineCodeExecutor, DockerCommandLineCodeExecutor

# Create a temporary directory to store the code files.
temp_dir = tempfile.TemporaryDirectory()

# Create a local command line code executor.
executor = LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir= temp_dir.name,  # Use the temporary directory to store the code files.
)



# Create an agent with code executor configuration.
code_executor_agent = ConversableAgent(
    "code_executor_agent",
    llm_config=False,  # Turn off LLM for this agent.
    code_execution_config={"executor": executor},  # Use the local command line code executor.
    human_input_mode="NEVER",  # Always take human input for this agent for safety.
)

message_with_code_block = """This is a message with code block.
The code block is below:
```python
import numpy as np
import matplotlib.pyplot as plt
x = np.random.randint(0, 100, 100)
y = np.random.randint(0, 100, 100)
plt.scatter(x, y)
plt.savefig('scatter.png')
print('Scatter plot saved to scatter.png')
```
This is the end of the message.
"""

# Generate a reply for the given code.
reply = code_executor_agent.generate_reply(messages=[{"role": "user", "content": message_with_code_block}])
print(reply)

import os
print(temp_dir.name)
print(os.listdir(temp_dir.name))
#temp_dir.cleanup()




### Demo a 2 agent chart summerizing a blog article

import logging
from autogen import ConversableAgent, AssistantAgent, UserProxyAgent
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


# Create assistant and user proxy agents
assistant = AssistantAgent(
    name="CTO",
    llm_config=llm_config,
    system_message="You are a chief technical officer of a technology company",
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "web"},
    llm_config=llm_config,
    system_message="""You are a professional blog writer and have very good command on English language.
    Reply TERMINATE if the task has been resolved to full satisfaction. 
    Otherwise, reply CONTINUE, or the reason why the task is not solved yet."""
)

# Define task
task = """
Find out how the Ramayan mythology story passed down from it occurance to till date.
What's the historical and archaeological evidences available? 
Provide the evidences with timeline.
"""

class TaskHandler:
    def __init__(self, task):
        self.task = task

    def run(self, user_proxy, assistant):
        """
        Initiates a chat with the assistant for the given task.

        Args:
            user_proxy (UserProxyAgent): The user proxy agent.
            assistant (AssistantAgent): The assistant agent.
        """
        user_proxy.initiate_chat(assistant, message=self.task)

# Initialize task handler and run the task
task_handler = TaskHandler(task)
task_handler.run(user_proxy, assistant)

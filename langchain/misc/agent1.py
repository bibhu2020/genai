# This is demonstration of agent to read real-time weather data
## using TAVILY engine to search the result from the internet.
## Tavily's Search API is a search engine built specifically for AI agents (LLMs), delivering real-time, accurate, and factual results at speed.


from langchain_core.output_parsers import StrOutputParser
parser = StrOutputParser()

## Configure the LLM
from langchain.utility.llm_factory2 import LLMFactory
llm = LLMFactory.get_llm("azure")

## Import relevant functionality
from langchain_core.messages import HumanMessage

## Creating a memory saver to save the checkpoint or conversation history
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

## Define the tools to use
from langchain_community.tools.tavily_search import TavilySearchResults
search = TavilySearchResults(max_results=1)
search_results = search.invoke("what is the weather in SF")
print(search_results)
# If we want, we can create other tools.
# Once we have all the tools we want, we can put them in a list that we will reference later.
tools = [search]

## Bind the tools to the LLM
llm_with_tools = llm.bind_tools(tools)

## Here is call to LLM which does not invoke the tools or tell the tool to be used.
response = llm_with_tools.invoke([HumanMessage(content="Hi!")])
print(f"ContentString: {response.content}")
print(f"ToolCalls: {response.tool_calls}")

## Here is call to LLM which tells the tool to be used.
## But you will notice that the llm is only suggesting the tools to be invoked, NOT invoking the tool
response = llm_with_tools.invoke([HumanMessage(content="What's the weather in SF?")])
print(f"ContentString: {response.content}")
print(f"ToolCalls: {response.tool_calls}")

######NOTE: The above code is just to demonstrates that LLM only helps to suggest the tools to be invoked, NOT invoking the tool.
######      The actual invocation of the tool is done by the agent. So, let's create an agent to invoke the tool.

## Create the agent with the tools and memory saver
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(llm, tools, checkpointer=memory)

config = {"configurable": {"thread_id": "abc123"}} # this is like a session id

## Option#1: Run the agent with the same message as above and read the output
response = agent.invoke({"messages": [HumanMessage(content="What's the weather in SF?")]}, config)
print(response["messages"])

## Option#2: Streaming the output from the agent (this is for not to wait for the agent to complete processing)
for chunk in agent.stream(
    {"messages": [HumanMessage(content="whats the weather in sf?")]}, config
):
    print(chunk)
    print("----")
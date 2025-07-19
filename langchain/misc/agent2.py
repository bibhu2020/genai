# This is demonstration of agent to read real-time weather data
## using TAVILY engine to search the result from the internet.
## Tavily's Search API is a search engine built specifically for AI agents (LLMs), delivering real-time, accurate, and factual results at speed.
## This is the same as agent1.py but it shows how to use the agent streams output asynchrously.

from langchain_core.output_parsers import StrOutputParser
parser = StrOutputParser()

## Configure the LLM
from langchain.utility.llm_factory2 import LLMFactory
llm = LLMFactory.get_llm("azure")

## Import relevant functionality
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

## Define the tools to use
from langchain_community.tools.tavily_search import TavilySearchResults
search = TavilySearchResults(max_results=1)
tools = [search]

## Bind the tools to the LLM
llm_with_tools = llm.bind_tools(tools)

## Create the agent
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(llm, tools)

## Option#3: Streaming the output from the agent asynchrously (this is for not to wait for the agent to complete processing)
async def main():
    async for event in agent.astream_events(
        {"messages": [HumanMessage(content="whats the weather in sf?")]}, version="v1"
    ):
        kind = event["event"]
        if kind == "on_chain_start":
            if (
                event["name"] == "Agent"
            ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                print(
                    f"Starting agent: {event['name']} with input: {event['data'].get('input')}"
                )
        elif kind == "on_chain_end":
            if (
                event["name"] == "Agent"
            ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                print()
                print("--")
                print(
                    f"Done agent: {event['name']} with output: {event['data'].get('output')['output']}"
                )
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                # Empty content in the context of OpenAI means
                # that the model is asking for a tool to be invoked.
                # So we only print non-empty content
                print(content, end="")
        elif kind == "on_tool_start":
            pass
            #print("--")
            #print(f"Starting tool: {event['name']} with inputs: {event['data'].get('input')}")
        elif kind == "on_tool_end":
            pass
            #print(f"Done tool: {event['name']}")
            #print(f"Tool output was: {event['data'].get('output')}")
            #print("--")

import asyncio
asyncio.run(main())
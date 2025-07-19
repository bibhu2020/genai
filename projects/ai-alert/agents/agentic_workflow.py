
from typing import TypedDict, Annotated, Sequence, Optional
from langgraph.graph.message import add_messages # Is reducer function that just aggregrates the messages.
from langchain_core.messages import BaseMessage, HumanMessage # base message class
from utils.model_loader import ModelLoader
from prompt_library.prompt import SYSTEM_PROMPT
from langgraph.graph import StateGraph, END, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from datetime import datetime

from tools.log_query_tool import LogQueryTool
from tools.notification_tool import NotificationTool

class AgentState(TypedDict):
    # messages is a list (or other sequence) of BaseMessage objects, and it has extra metadata attached to it: add_messages
    ## Sequence is a type hint that represents any ordered, iterable collection of items — like lists, tuples, or strings 
    ## Annotated type lets you attach metadata to a type. It's not used by Python itself, but frameworks (like LangGraph, Pydantic, FastAPI) can use it.
    messages: Annotated[Sequence[BaseMessage], add_messages]
    appName: str
    incidentTime: datetime  # ✅ FIXED
    sendNotification: bool
    severity: str
    logs: Optional[str]  # to store log output from query tool
    analysis: Optional[str]  # to store LLM analysis before notification

class GraphBuilder():
    def __init__(self,model_provider: str = "azureopenai"):
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm()
        
        self.tools = []
        
        self.log_query_tool = LogQueryTool()
        self.notification_tool = NotificationTool()
        
        self.tools.extend([* self.log_query_tool.log_query_tool_list, 
                           * self.notification_tool.notification_tool_list])
        
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)
        
        self.graph = None
        
        self.system_prompt = SYSTEM_PROMPT
    
    
    # Node function
    def agent_function(self,state: AgentState) -> AgentState:
        """Main agent function"""
        print("\n[AGENT] Received messages:")
        for msg in state["messages"]:
            print(f"{msg.type}: {msg.content}")
        response = self.llm_with_tools.invoke([self.system_prompt] + state['messages'])
        print(f"[AGENT] LLM Response: {response.content}")
        return {
            "messages": [response],
            "appName": state["appName"],
            "incidentTime": state["incidentTime"],
            "sendNotification": state["sendNotification"],
            "severity": state["severity"]
        } # add_message() takes care of appending the message


    def should_continue(self, state: AgentState) -> AgentState:
        messages = state['messages']
        last_message = messages[-1]
        if not last_message.tool_calls:
            # print("[GRAPH] No tool calls. Ending.")
            return "end"
        else:
            # print(f"[GRAPH] Tool call detected: {[tc.name for tc in last_message.tool_calls]}")
            return "continue"

    def build_graph(self):
        graph_builder=StateGraph(AgentState)
        graph_builder.add_node("sre_agent", self.agent_function)
        graph_builder.add_edge(START,"sre_agent")

        graph_builder.add_node("tools", ToolNode(tools=self.tools))

        graph_builder.add_conditional_edges(
            source="sre_agent",
            path=self.should_continue,
            path_map={
                # Edge: Node
                "end": END,
                "continue": "tools"
            }
        )

        graph_builder.add_edge("tools", "sre_agent")

        self.graph = graph_builder.compile()
        return self.graph


    def __call__(self):
        return self.build_graph()
# mcp_connector.py
import os
import asyncio
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

load_dotenv()

# (Optional) Azure OpenAI setup if you mix chat + tools
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)
openai_client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2024-04-01-preview",
    azure_ad_token_provider=token_provider
)

# Use the base server URL; the client library will GET /sse and POST to /messages under the hood
SERVER_URL = "http://localhost:5008"

class MCPConnector:
    def __init__(self, server_url: str = SERVER_URL):
        self._server_url    = server_url
        self._transport_mgr = None    # streamablehttp_client context manager
        self._session_mgr   = None    # ClientSession context manager
        self._session       = None    # actual MCP session
        self.tools          = {}

    async def start(self):
        """
        1) Enter the SSE transport context to get (read, write, meta)
        2) Wrap those streams in a ClientSession to get the RPC session
        3) Initialize and discover available tools
        """
        # Step 1: connect via SSE transport
        self._transport_mgr = streamablehttp_client(self._server_url)
        read_stream, write_stream, _meta = await self._transport_mgr.__aenter__()

        # Step 2: wrap in ClientSession
        self._session_mgr = ClientSession(read_stream, write_stream)
        self._session     = await self._session_mgr.__aenter__()

        # Step 3: perform JSON-RPC handshake and list tools
        await self._session.initialize()
        resp = await self._session.list_tools()
        self.tools = {t.name: t for t in resp.tools}

    async def call_tool(self, tool_name: str, args: dict):
        """
        Invoke a specific tool by name with the given args.
        """
        if not self._session:
            raise RuntimeError("Session not started. Call start() first.")
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name!r} not available. Available: {list(self.tools)}")
        result = await self._session.call_tool(tool_name, args)
        return result.content

    async def stop(self):
        """
        Exit both the ClientSession and transport contexts cleanly.
        """
        if self._session_mgr:
            await self._session_mgr.__aexit__(None, None, None)
        if self._transport_mgr:
            await self._transport_mgr.__aexit__(None, None, None)

def run_coro(coro):
    """
    Helper to run an async coroutine from a synchronous context.
    """
    return asyncio.get_event_loop().run_until_complete(coro)
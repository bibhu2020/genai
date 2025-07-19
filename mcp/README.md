# MCP
MCP is an open protocol that standardizes how applications provide context to LLMs. Think of MCP like a USB-C port for AI applications. Just as USB-C provides a standardized way to connect your devices to various peripherals and accessories, MCP provides a standardized way to connect AI models to different data sources and tools.


## MCP Architecture
At its core, MCP follows a client-server architecture where a host application can connect to multiple servers:

- MCP Hosts: Programs like Claude Desktop, IDEs, or AI tools that want to access data through MCP
- MCP Clients: Protocol clients that maintain 1:1 connections with servers
- MCP Servers: Lightweight programs that each expose specific capabilities through the standardized Model Context Protocol
- Local Data Sources: Your computer’s files, databases, and services that MCP servers can securely access
- Remote Services: External systems available over the internet (e.g., through APIs) that MCP servers can connect to

Reference# https://modelcontextprotocol.io/introduction

## Core Concepts of MCP Server
It has 3 main capabilities:

1. Resources: File-like data that can be read by clients (like API responses or file contents)

2. Tools: Functions that can be called by the LLM (with user approval)

3. Prompts: Pre-written templates that help users accomplish specific tasks


## Creating a Server Exposing Tool that reads and forecasts weather 
```sh
# Create a new directory for our project
uv init weather
cd weather

# Create virtual environment and activate it
uv venv
source .venv/bin/activate

# Install dependencies
uv add "mcp[cli]" httpx

# Create our server file
touch weather.py
```
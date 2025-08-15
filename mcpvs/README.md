# MCP Server Setup on VS Code

## Installation Guide
https://github.com/microsoft/azure-devops-mcp

## Pre-requisites
- nodejs
- az cli

```bash
sudo apt update
sudo apt upgrade -y

# Remove old nodejs package
sudo apt remove -y nodejs

# Add NodeSource repository (replace 20.x with desired major version)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

node -v

echo 'export PATH=$PATH:/usr/bin' >> ~/.bashrc
source ~/.bashrc

sudo apt install ca-certificates curl apt-transport-https lsb-release gnupg -y

curl -sL https://packages.microsoft.com/keys/microsoft.asc | \
    gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null

AZ_REPO=$(lsb_release -cs)
echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | \
    sudo tee /etc/apt/sources.list.d/azure-cli.list

sudo apt update
sudo apt install azure-cli -y

az version

```

## Steps

1. Login to Azure `az login --use-device-code`

2. Install Azure DevOps MCP CLI tool globally
This tool provides command-line utilities for interacting with Azure DevOps Model Context Protocol (MCP) resources, such as registering servers, managing connections, and performing MCP-related operations.

It does not start the MCP server itself. Instead, it is used for MCP management tasks and automation, not for running the server. To run the server, you need to install and use @microsoft/mcp-server.

```bash
sudo npm install -g npm@11.5.2

sudo npm install -g @azure-devops/mcp

```

3. Run the MCP server where the mcp.json is located
```bash
az login --use-device-code

cd ./mcpvs

mcp-server --config mcp.json

```

3.
```
npm init -y

npm install -g @microsoft/mcp-server

mcp-server --config mcp.json
```
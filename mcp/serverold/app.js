import { McpClient } from "@modelcontextprotocol/sdk/client/mcp.js";
// import { McpClient } from "@modelcontextprotocol/sdk/client.js"; 
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function run() {
  const client = new McpClient();

  // Connect over stdio (to the server process started alongside)
  const transport = new StdioClientTransport();
  await client.connect(transport);

  // Build the input query for your application
  const input = {
    applicationName: "my-app", // <-- replace with your app name
    timespanHours: 24,
    // workspaceId: "<optional-log-analytics-workspace-id>",
  };

  // Call the MCP server tool
  const response = await client.call("getApplicationDiagnostics", input);

  // Response content is an array of typed payloads
  for (const part of response.content) {
    if (part.type === "json") {
      console.log("JSON Result:", JSON.stringify(part.json, null, 2));
    } else if (part.type === "text") {
      console.log("Text Result:", part.text);
    }
  }

  // Clean up connection
  await client.dispose();
}

run().catch((err) => {
  console.error("Error in MCP client:", err);
  process.exit(1);
});

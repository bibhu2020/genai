// azure-mcp-server.js
//
// MCP server that queries Log Analytics, Activity Log, Deployments and links results
// Usage: MCP client calls "getApplicationDiagnostics" with { applicationName: "my-app" }

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import {
  AzureCliCredential,
  DefaultAzureCredential,
  InteractiveBrowserCredential,
} from "@azure/identity";
import { LogsQueryClient } from "@azure/monitor-query";
import { MonitorClient } from "@azure/arm-monitor";
import { ResourceManagementClient } from "@azure/arm-resources";
import { WebSiteManagementClient } from "@azure/arm-appservice";
import { LogicManagementClient } from "@azure/arm-logic";
// import { ContainerServiceClient } from "@azure/arm-containerservice"; // optional AKS-specific

const subscriptionId = process.env.AZURE_SUBSCRIPTION_ID;
if (!subscriptionId) {
  console.warn(
    "Warning: AZURE_SUBSCRIPTION_ID not set. Some calls require subscription context."
  );
}

// Authentication helper: prefer Azure CLI -> Default credential -> Interactive browser (fallback)
function getCredential() {
  try {
    // If Azure CLI is available and logged-in, this will work
    return new AzureCliCredential();
  } catch (e) {
    // fall through
  }
  // DefaultAzureCredential will chain env / managed identity / etc.
  return new DefaultAzureCredential();
}

// Helper: build clients
function makeClients() {
  const cred = getCredential();
  const logsClient = new LogsQueryClient(cred);
  const monitorClient = new MonitorClient(cred, subscriptionId);
  const resourceClient = new ResourceManagementClient(cred, subscriptionId);
  const webSiteClient = new WebSiteManagementClient(cred, subscriptionId);
  const logicClient = new LogicManagementClient(cred, subscriptionId);
  return { cred, logsClient, monitorClient, resourceClient, webSiteClient, logicClient };
}

// Utility: find resources that match an application name in tags / name
async function findResourcesByName(resourceClient, applicationName) {
  const matches = [];
  const lowerApp = (applicationName || "").toLowerCase();
  for await (const r of resourceClient.resources.list()) {
    const lowerName = (r.name || "").toLowerCase();
    const tagMatch =
      r.tags &&
      Object.values(r.tags).some((v) => v && String(v).toLowerCase().includes(lowerApp));
    if (lowerName.includes(lowerApp) || tagMatch) {
      matches.push({
        id: r.id,
        name: r.name,
        type: r.type,
        location: r.location,
        tags: r.tags,
        properties: r.properties || {},
      });
    }
  }
  return matches;
}

// Activity log query: for a list of resourceIds, get recent activity
async function getActivityLogs(monitorClient, resourceIds, timespanMinutes = 60 * 24) {
  const results = [];
  const toTime = new Date();
  const fromTime = new Date(Date.now() - timespanMinutes * 60 * 1000);
  const filterBase = `eventTimestamp ge '${fromTime.toISOString()}' and eventTimestamp le '${toTime.toISOString()}'`;
  for (const rid of resourceIds) {
    const filter = `${filterBase} and resourceId eq '${rid}'`;
    // monitorClient.activityLogs.list accepts an options object with filter
    for await (const ev of monitorClient.activityLogs.list({ filter })) {
      results.push(ev);
    }
  }
  return results;
}

// Query Log Analytics using Kusto query text
// Uses explicit startTime/endTime (works with current @azure/monitor-query API)
async function queryLogAnalytics(logsClient, workspaceId, kustoQuery, timespanHours = 24) {
  if (!workspaceId) throw new Error("workspaceId required for Log Analytics query");
  const endTime = new Date();
  const startTime = new Date(Date.now() - timespanHours * 60 * 60 * 1000);

  // queryWorkspace(workspaceId, query, options) is supported
  // options object: { startTime, endTime }
  const res = await logsClient.queryWorkspace(workspaceId, kustoQuery, {
    startTime,
    endTime,
  });
  return res;
}

// Try to discover a Log Analytics workspace for a resource (basic heuristic)
async function discoverWorkspaceForResource(resourceClient, resource) {
  // Many resources route diagnostics to a workspace via Diagnostic Settings.
  // Implementing full diagnostic-settings discovery requires the Monitor management API.
  // For now: allow override via env var.
  if (process.env.LOG_WORKSPACE_ID) return process.env.LOG_WORKSPACE_ID;
  return null;
}

// Get App Service / Function App deployments (KUDU / deployments)
async function getAppServiceDeployments(webSiteClient, resource) {
  try {
    const parts = resource.id.split("/");
    const rgIndex = parts.indexOf("resourceGroups");
    if (rgIndex < 0) return [];
    const rg = parts[rgIndex + 1];
    const name = parts[parts.length - 1];
    const deployments = [];

    // Different SDK versions expose different helpers. Try common variants defensively.
    if (webSiteClient.webApps && webSiteClient.webApps.listDeployments) {
      for await (const d of webSiteClient.webApps.listDeployments(rg, name)) {
        deployments.push(d);
      }
    } else if (webSiteClient.webApps && webSiteClient.webApps.list) {
      // fallback: list the web app metadata (not deployments) - keep minimal info
      const meta = await webSiteClient.webApps.get(rg, name);
      deployments.push({ note: "webApp metadata - deployments API not present in this SDK version", meta });
    } else {
      // no-op
    }

    return deployments;
  } catch (e) {
    console.warn("getAppServiceDeployments error", e.message || e);
    return [];
  }
}

// Get Logic App runs (basic)
async function getLogicAppRuns(logicClient, resource) {
  try {
    const parts = resource.id.split("/");
    const rgIndex = parts.indexOf("resourceGroups");
    if (rgIndex < 0) return [];
    const rg = parts[rgIndex + 1];
    const name = parts[parts.length - 1];
    const runs = [];

    if (logicClient.workflowRuns && logicClient.workflowRuns.list) {
      for await (const run of logicClient.workflowRuns.list(rg, name)) {
        runs.push(run);
      }
    } else {
      // SDK doesn't have workflowRuns in this version
    }

    return runs;
  } catch (e) {
    console.warn("getLogicAppRuns error", e.message || e);
    return [];
  }
}

// Correlate logs / activity / deployments by resourceId and times
function correlateData(resources, logsTables, activityLogs, deployments, logicRuns) {
  const byId = {};
  for (const r of resources) {
    byId[r.id] = { resource: r, logs: [], activity: [], deployments: [], logicRuns: [] };
  }

  for (const a of activityLogs || []) {
    const target = byId[a.resourceId];
    if (target) target.activity.push(a);
  }

  for (const d of deployments || []) {
    const rid = d.resourceId || d.id || d.properties?.siteName || null;
    for (const key of Object.keys(byId)) {
      try {
        if (
          rid &&
          (String(key).toLowerCase().includes(String(rid).toLowerCase()) ||
            (byId[key].resource.name &&
              String(d.id || "").toLowerCase().includes(byId[key].resource.name.toLowerCase())))
        ) {
          byId[key].deployments.push(d);
        }
      } catch (e) {
        // ignore per-item errors
      }
    }
  }

  for (const run of logicRuns || []) {
    for (const key of Object.keys(byId)) {
      if (String(run.id || "").toLowerCase().includes(key.toLowerCase())) {
        byId[key].logicRuns.push(run);
      }
    }
  }

  return { byId, logsTables, meta: { activityCount: (activityLogs || []).length, deploymentCount: (deployments || []).length } };
}

// Build MCP server and expose tool
async function main() {
  const { cred, logsClient, monitorClient, resourceClient, webSiteClient, logicClient } = makeClients();

  const server = new McpServer({ name: "azure-mcp", version: "1.0.0" });

  server.registerTool(
    "getApplicationDiagnostics",
    {
      title: "Get Application Diagnostics",
      description: "Return logs, activity, and deployment info for application name",
      inputSchema: {
        type: "object",
        properties: {
          applicationName: { type: "string" },
          timespanHours: { type: "number", default: 24 },
          workspaceId: { type: "string" }, // optional override
        },
        required: ["applicationName"],
      },
    },
    async (params) => {
      const app = params.applicationName;
      const timespanHours = params.timespanHours || 24;
      const workspaceId = params.workspaceId || process.env.LOG_WORKSPACE_ID;

      // 1) find candidate resources
      const resources = await findResourcesByName(resourceClient, app);

      // 2) prepare resourceIds
      const resourceIds = resources.map((r) => r.id);

      // 3) activity logs
      const activityLogs = await getActivityLogs(monitorClient, resourceIds, timespanHours * 60);

      // 4) deployments for App Services & Functions
      const allDeployments = [];
      const allLogicRuns = [];
      for (const r of resources) {
        if (r.type && r.type.toLowerCase().includes("microsoft.web/sites")) {
          const d = await getAppServiceDeployments(webSiteClient, r);
          allDeployments.push(...(d || []));
        }
        if (r.type && r.type.toLowerCase().includes("microsoft.logic/workflows")) {
          const runs = await getLogicAppRuns(logicClient, r);
          allLogicRuns.push(...(runs || []));
        }
      }

      // 5) Log Analytics queries (example queries)
      const logsTables = [];
      if (workspaceId) {
        const queries = [
          {
            name: "AppServiceHttpLogs",
            kusto: `AppRequests | where TimeGenerated >= ago(${timespanHours}h) | where Resource contains "${app}" | top 500 by TimeGenerated desc`,
          },
          {
            name: "FunctionLogs",
            kusto: `AppTraces | where TimeGenerated >= ago(${timespanHours}h) | where Resource contains "${app}" | top 500 by TimeGenerated desc`,
          },
          {
            name: "ContainerLogs",
            kusto: `ContainerLog | where TimeGenerated >= ago(${timespanHours}h) | where ClusterName contains "${app}" or ContainerName contains "${app}" | top 500 by TimeGenerated desc`,
          },
        ];

        for (const q of queries) {
          try {
            const r = await queryLogAnalytics(logsClient, workspaceId, q.kusto, timespanHours);
            logsTables.push({ name: q.name, result: r });
          } catch (e) {
            logsTables.push({ name: q.name, error: e.message || String(e) });
          }
        }
      } else {
        // try discover
        const discovered = resources.length ? await discoverWorkspaceForResource(resourceClient, resources[0]) : null;
        if (discovered) {
          // You could run the same queries against discovered workspace
        } else {
          // no workspace: note it
        }
      }

      // 6) correlate data
      const correlated = correlateData(resources, logsTables, activityLogs, allDeployments, allLogicRuns);

      // 7) return structured response
      return {
        content: [
          {
            type: "json",
            json: {
              resources,
              activityLogsCount: (activityLogs || []).length,
              deploymentsCount: allDeployments.length,
              logicRunsCount: allLogicRuns.length,
              correlated,
            },
          },
          { type: "text", text: `Found ${resources.length} resources, ${(activityLogs || []).length} activity events, ${allDeployments.length} deployments.` },
        ],
      };
    }
  );

  // Connect with stdio transport (works well with VS Code MCP client)
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // Process remains alive while MCP server is connected
}

// top-level run
main().catch((err) => {
  console.error("Fatal error in MCP server:", err);
  process.exit(1);
});

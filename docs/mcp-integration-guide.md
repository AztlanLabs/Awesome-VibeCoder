# Model Context Protocol (MCP) Integration Guide

This guide explains how to integrate external Model Context Protocol (MCP) servers with custom agents and workflows. MCP allows agents to securely interact with database engines, external APIs, security scanners, and custom scripts.

---

## 1. Declarative MCP Server Configuration

To map an MCP server to an agent, declare it directly in the agent's YAML frontmatter under the `mcp-servers` block. 

### Stdio Connection Schema
The system maps MCP servers using standard input/output (stdio) connection models:

```yaml
---
name: security-agent
description: Specialized agent for scanning vulnerabilities using local and cloud tools.
mcp-servers:
  trivy-analyzer:
    type: local
    command: npx
    args: ['-y', '@aquasecurity/trivy-mcp']
    tools: ['*']
    env:
      TRIVY_API_KEY: ${{ secrets.COPILOT_MCP_TRIVY_KEY }}
---
```

### Configuration Fields
* **`type`**: Execution environment (typically `local`).
* **`command`**: Execution command/executable (e.g., `npx`, `python3`, `node`).
* **`args`**: List of string arguments to pass to the connection process.
* **`tools`**: Restricts tool execution privileges. Use `['*']` to grant access to all tools provided by the server, or list specific tool names (e.g., `['scan-image', 'list-vulnerabilities']`).
* **`env`**: Environment variables passed to the server process.

---

## 2. Secure Environment Variables & Secrets

To maintain strict security boundaries, the runner restricts which repository secrets are exposed to local MCP execution runtimes:

> [!IMPORTANT]
> **Secret Prefix Constraints**:
> - All repository secrets mapped into an MCP environment block must be prefixed with **`COPILOT_MCP_`**.
> - Secrets that do not match this prefix are filtered out by the host process and will not be made available to the MCP server.

### Example Secrets Mapping
```yaml
env:
  API_TOKEN: ${{ secrets.COPILOT_MCP_API_TOKEN }}         # SUCCESS: Allowed access
  DB_PASSWORD: ${{ secrets.DATABASE_PRODUCTION_PASSWORD }} # FAILURE: Filtered out (invalid prefix)
```

---

## 3. Tool Namespacing & Aliasing

When multiple MCP servers are configured within the same agent context, naming collisions can occur if different servers expose tools with the same name. To prevent this:

- All MCP tools are namespaced by the host using their server name as a prefix:
  `[server-name]/[tool-name]`
- Example: If a server named `trivy-analyzer` exposes a tool named `scan-image`, the agent invokes it as:
  `trivy-analyzer/scan-image`

---

## 4. MCP Server Deployment Patterns

### Pattern A: Standard npm Packages
For widely-used open-source tools with npm MCP wrappers, utilize `npx -y` to run the package directly:
```yaml
mcp-servers:
  sqlite-helper:
    type: local
    command: npx
    args: ['-y', '@modelcontextprotocol/server-sqlite', '--db', './my-db.sqlite']
```

### Pattern B: Custom Local Scripts
For project-specific internal scripts, configure the stdio engine to execute local Node/Python scripts directly:
```yaml
mcp-servers:
  local-schema-validator:
    type: local
    command: node
    args: ['./scripts/schema-mcp-server.js']
```

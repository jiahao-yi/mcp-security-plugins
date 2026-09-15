# MCP Security Plugins

Small, host-side plugins for safer MCP tool discovery.

## Packages

### `mcp-tools-list-plugin`

- Gives every tool a Host-owned, server-qualified name.
- Treats `description` and `inputSchema` text as untrusted data.
- Prevents tool-name collisions without calling an LLM.

```python
from mcp_tools_list_plugin import ToolsListBoundaryPlugin, server_name_hash_label

plugin = ToolsListBoundaryPlugin()
result = await plugin.on_tools_list(
    server_id="github-connection-1",
    server_label=server_name_hash_label("github-connection-1"),
    tools=tools,
)

# Example model-facing name: github_connection_1_<hash>__get_file_contents
safe_tools = result.tools
route = plugin.resolve(safe_tools[0]["name"])
```

### `mcp-probe-plugin`

- Asks a small model to build bounded test arguments.
- Validates arguments before the tool call.
- Compares the visible result with the advertised capability.
- Returns `admit_observed`, `reject`, or `inconclusive`.

```python
from mcp_probe_plugin import ToolsListProbePlugin

plugin = ToolsListProbePlugin(planner=model, judge=model)
report = await plugin.on_tools_list(
    server_id="filesystem-test",
    tools=tools,
    probe_executor=sandbox.call_tool,
    fixture=trusted_fixture,
    call_policy=host_policy,
)
```

The caller must provide the sandbox and authorization policy. A successful
probe only shows consistency for the tested input and visible result; it does
not certify that a server is safe.

## Install

```bash
pip install -e packages/mcp-tools-list-plugin
pip install -e 'packages/mcp-probe-plugin[openai,mcp]'
```

## Test

```bash
PYTHONPATH=packages/mcp-tools-list-plugin/src python -m unittest discover -s packages/mcp-tools-list-plugin/tests
PYTHONPATH=packages/mcp-probe-plugin/src python -m unittest discover -s packages/mcp-probe-plugin/tests
```

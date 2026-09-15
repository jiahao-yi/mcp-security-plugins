# mcp-tools-list-plugin

An `on_tools_list` plugin that gives MCP tools Host-owned, server-qualified
names and declares tool descriptions and schema text to be untrusted data.

```python
from mcp_tools_list_plugin import ToolsListBoundaryPlugin, server_name_hash_label

plugin = ToolsListBoundaryPlugin()
result = await plugin.on_tools_list(
    server_id="connection-1",
    server_label=server_name_hash_label("connection-1"),
    tools=tools,
)
```

Call `plugin.resolve(model_tool_name)` before dispatch to recover the original
server ID and local tool name.

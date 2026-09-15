# mcp-probe-plugin

An `on_tools_list` plugin for bounded checks of advertised MCP capabilities.
It validates model-generated arguments, calls a caller-provided sandbox, and
checks the judge's evidence against the visible result.

```python
from mcp_probe_plugin import ToolsListProbePlugin

plugin = ToolsListProbePlugin(planner=model, judge=model)
report = await plugin.on_tools_list(
    server_id="test-server",
    tools=tools,
    probe_executor=sandbox.call_tool,
    fixture=trusted_fixture,
    call_policy=host_policy,
)
```

The result measures observed metadata/result consistency. The Host remains
responsible for sandboxing and authorization.


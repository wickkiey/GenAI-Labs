# MCP Assistant

This project wraps the lab's MCP servers behind a single chat interface.

What I built: a shell that routes user requests to the correct MCP server capability.
What surprised me: server routing is often the hardest part, not the tool logic itself.
What broke: name collisions across tools become visible as soon as multiple servers are connected.

import asyncio
from typing import Optional
from contextlib import AsyncExitStack
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.stdio = None
        self.write = None

    async def connect(self, server_script_path: str):
        command = "python"
        server_params = StdioServerParameters(command=command, args=[server_script_path], env=None)
        self.stdio, self.write = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

    async def list_tools(self):
        if not self.session:
            raise RuntimeError("MCP session not connected")
        response = await self.session.list_tools()
        return response.tools

    async def call_tool(self, tool_name, tool_input=None):
        if not self.session:
            raise RuntimeError("MCP session not connected")
        return await self.session.call_tool(tool_name, tool_input or {})

    async def cleanup(self):
        await self.exit_stack.aclose()

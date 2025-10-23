import asyncio
import os
import sys
from typing import Optional, Dict, Any, List
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from anthropic import Anthropic

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()


class MCPClient:
    def __init__(self) -> None:
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        # Anthropic client; expects ANTHROPIC_API_KEY in env
        self.anthropic = Anthropic()
        self.stdio = None
        self.write = None

    async def connect_to_server(self, server_script_path: str) -> None:
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        # Use the current Python interpreter to spawn the server
        command = sys.executable if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None,
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        tools_resp = await self.session.list_tools()
        tool_names = [tool.name for tool in tools_resp.tools]
        print("\nConnected to server with tools:", tool_names)

    async def process_query(self, query: str) -> str:
        if not self.session:
            raise RuntimeError("Client not connected to server")

        messages: List[Dict[str, Any]] = [
            {"role": "user", "content": query}
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema,
        } for tool in response.tools]

        # First call to Claude
        claude_msg = self.anthropic.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            max_tokens=1000,
            messages=messages,
            tools=available_tools,
        )

        final_text: List[str] = []

        assistant_message_content: List[Dict[str, Any]] = []
        for content in claude_msg.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append({"type": "text", "text": content.text})
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                try:
                    result = await self.session.call_tool(tool_name, tool_args)
                except Exception as e:
                    result_content = [{"type": "text", "text": f"Tool {tool_name} failed: {e}"}]
                else:
                    result_content = result.content

                final_text.append(f"[Called tool {tool_name}]")

                assistant_message_content.append({
                    "type": "tool_use",
                    "id": content.id,
                    "name": tool_name,
                    "input": tool_args,
                })

                messages.append({"role": "assistant", "content": assistant_message_content})
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": result_content,
                    }]
                })

                claude_msg = self.anthropic.messages.create(
                    model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools,
                )

                # Append next text if present
                for nxt in claude_msg.content:
                    if nxt.type == 'text':
                        final_text.append(nxt.text)

        return "\n".join(final_text)

    async def chat_loop(self) -> None:
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print("\n" + response)
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self) -> None:
        await self.exit_stack.aclose()


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

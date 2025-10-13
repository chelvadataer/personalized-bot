import asyncio
import os
import sys

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main() -> None:
    command = sys.executable
    args = [os.path.join(os.getcwd(), "server.py")]

    async with stdio_client(StdioServerParameters(command=command, args=args)) as (read_stream, write_stream):
        session = ClientSession(read_stream, write_stream)
        await session.initialize()

        tools = await session.list_tools()
        print("Available tools:", [t.name for t in tools.tools])

        call = await session.call_tool("echo", {"message": "hello world"})
        texts = [c.text for c in call.content if getattr(c, "type", "") == "text"]
        print("Tool response:", " ".join(texts))


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from mcp.server import Server
from mcp.types import TextContent, Tool, ToolRequest
from mcp.server.stdio import stdio_server


async def main() -> None:
    server = Server(name="example-echo-server")

    @server.tool()
    async def echo(message: str) -> list[TextContent]:
        return [TextContent(type="text", text=f"echo: {message}")]

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

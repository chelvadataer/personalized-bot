import asyncio
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from .services import mcp  # FastMCP instance with tools


app = FastAPI(title="Cab MCP Server")


@app.on_event("startup")
async def startup_event():
    # Start MCP server in background
    asyncio.create_task(mcp.start())


if __name__ == "__main__":
    # When executed directly, run MCP over stdio
    asyncio.run(mcp.start())

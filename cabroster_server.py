import asyncio
import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

CABROSTER_API_BASE = os.getenv("CABROSTER_API_BASE", "https://api.cabroster.example.com")
CABROSTER_API_KEY = os.getenv("CABROSTER_API_KEY", "")

server = FastMCP("cabroster")


async def _http_client() -> httpx.AsyncClient:
    headers = {}
    if CABROSTER_API_KEY:
        headers["Authorization"] = f"Bearer {CABROSTER_API_KEY}"
    return httpx.AsyncClient(base_url=CABROSTER_API_BASE, headers=headers, timeout=30.0)


@server.tool()
async def health() -> Dict[str, Any]:
    """Check server and Cabroster backend health."""
    async with await _http_client() as client:
        try:
            r = await client.get("/health")
            r.raise_for_status()
            return {"status": "ok", "cabroster": r.json()}
        except httpx.HTTPError as e:
            return {"status": "error", "error": str(e)}


@server.tool()
async def list_rosters(date: Optional[str] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """List rosters. date format: YYYY-MM-DD (optional)."""
    params: Dict[str, Any] = {"limit": limit, "offset": offset}
    if date:
        params["date"] = date
    async with await _http_client() as client:
        r = await client.get("/rosters", params=params)
        r.raise_for_status()
        return r.json()


@server.tool()
async def get_roster(roster_id: str) -> Dict[str, Any]:
    """Get roster details by ID."""
    async with await _http_client() as client:
        r = await client.get(f"/rosters/{roster_id}")
        r.raise_for_status()
        return r.json()


@server.tool()
async def create_roster(name: str, date: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Create a new roster."""
    payload = {"name": name, "date": date}
    if description:
        payload["description"] = description
    async with await _http_client() as client:
        r = await client.post("/rosters", json=payload)
        r.raise_for_status()
        return r.json()


@server.tool()
async def assign_driver(roster_id: str, driver_id: str, shift: str) -> Dict[str, Any]:
    """Assign a driver to a roster. shift example: morning/afternoon/night."""
    payload = {"driver_id": driver_id, "shift": shift}
    async with await _http_client() as client:
        r = await client.post(f"/rosters/{roster_id}/assignments", json=payload)
        r.raise_for_status()
        return r.json()


@server.tool()
async def list_rides(roster_id: Optional[str] = None, status: Optional[str] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """List rides filtered by roster_id and/or status."""
    params: Dict[str, Any] = {"limit": limit, "offset": offset}
    if roster_id:
        params["roster_id"] = roster_id
    if status:
        params["status"] = status
    async with await _http_client() as client:
        r = await client.get("/rides", params=params)
        r.raise_for_status()
        return r.json()


@server.tool()
async def get_ride(ride_id: str) -> Dict[str, Any]:
    """Get ride details by ID."""
    async with await _http_client() as client:
        r = await client.get(f"/rides/{ride_id}")
        r.raise_for_status()
        return r.json()


@server.tool()
async def update_ride_status(ride_id: str, status: str) -> Dict[str, Any]:
    """Update ride status (e.g., scheduled, en_route, completed, cancelled)."""
    payload = {"status": status}
    async with await _http_client() as client:
        r = await client.patch(f"/rides/{ride_id}", json=payload)
        r.raise_for_status()
        return r.json()


async def amain() -> None:
    # Run server over stdio using FastMCP helper
    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(amain())

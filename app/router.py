from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Annotated
import os
from .models import Cab, CabLocationUpdate
from .services import CabService

router = APIRouter(prefix="/api/cab_details", tags=["cabs"])


def verify_token(request: Request) -> None:
    expected = os.getenv("CAB_MCP_TOKEN")
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip() if auth_header else None
    if expected and token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


Auth = Annotated[None, Depends(verify_token)]


@router.get("/")
def get_all_cabs(request: Request, _: Auth = None):
    service = CabService(request)
    return service.get_all_cabs()


@router.post("/")
def add_cab(cab: Cab, request: Request, _: Auth = None):
    service = CabService(request)
    return service.add_cab(cab)


@router.put("/{cab_id}")
def update_cab(cab_id: int, cab: Cab, request: Request, _: Auth = None):
    service = CabService(request)
    return service.update_cab(cab_id, cab)


@router.delete("/{cab_id}")
def delete_cab(cab_id: int, request: Request, _: Auth = None):
    service = CabService(request)
    return service.delete_cab(cab_id)


@router.put("/{cab_id}/location")
def update_cab_location(cab_id: int, location: CabLocationUpdate, request: Request, _: Auth = None):
    service = CabService(request)
    return service.update_cab_location(cab_id, location)


@router.get("/{cab_id}")
def get_cab_location(cab_id: int, request: Request, _: Auth = None):
    service = CabService(request)
    return service.get_cab_location(cab_id)

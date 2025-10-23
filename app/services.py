from typing import Any, List, Dict
from fastapi import HTTPException, Request
from mcp.server.fastmcp import FastMCP
from .db import get_db
from .models import Cab, CabLocationUpdate


mcp = FastMCP("cab_roster_system")


class AuthUtils:
    def __init__(self, request: Request | None = None) -> None:
        self.request = request
        self.role = 1  # stubbed admin role
        self.user_id = 1  # stubbed user id


class CabService(AuthUtils):
    def __init__(self, request: Request | None = None):
        super().__init__(request)

    @mcp.tool()
    def get_all_cabs(self) -> List[Dict[str, Any]]:
        """Get all active cabs"""
        try:
            with get_db() as db:
                cursor = db.execute(
                    "SELECT * FROM cab_details WHERE is_deleted = 0"
                    if self.role == 1
                    else (
                        "SELECT c.* FROM cab_details c "
                        "JOIN cab_service s ON c.cab_model_id = s.cab_model_id "
                        "WHERE s.employee_id = ? AND c.is_deleted = 0 AND s.is_deleted = 0"
                    ),
                    () if self.role == 1 else (self.user_id,),
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:  # pragma: no cover
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    @mcp.tool()
    def add_cab(self, cab: Cab) -> Dict[str, str]:
        """Add a new cab"""
        try:
            with get_db() as db:
                db.execute(
                    "INSERT INTO cab_details (cab_model_name, cab_reg_name, is_deleted, created_date) "
                    "VALUES (?, ?, 0, datetime('now'))",
                    (cab.cab_model_name, cab.cab_reg_name),
                )
            return {"message": "Cab added successfully"}
        except Exception as e:  # pragma: no cover
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    @mcp.tool()
    def update_cab(self, cab_id: int, cab: Cab) -> Dict[str, str]:
        """Update an existing cab"""
        try:
            with get_db() as db:
                cur = db.execute(
                    "SELECT 1 FROM cab_details WHERE cab_model_id=? AND is_deleted=0",
                    (cab_id,),
                )
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Cab not found")

                res = db.execute(
                    "UPDATE cab_details SET cab_model_name=?, cab_reg_name=?, updated_date=datetime('now') "
                    "WHERE cab_model_id=? AND is_deleted=0",
                    (cab.cab_model_name, cab.cab_reg_name, cab_id),
                )
                if res.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Cab not found or no changes made")
            return {"message": "Cab updated successfully"}
        except HTTPException:
            raise
        except Exception as e:  # pragma: no cover
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    @mcp.tool()
    def delete_cab(self, cab_id: int) -> Dict[str, str]:
        """Soft delete a cab"""
        try:
            with get_db() as db:
                cur = db.execute(
                    "SELECT 1 FROM cab_details WHERE cab_model_id=? AND is_deleted=0",
                    (cab_id,),
                )
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Cab not found")

                res = db.execute(
                    "UPDATE cab_details SET is_deleted=1, updated_date=datetime('now') "
                    "WHERE cab_model_id=? AND is_deleted=0",
                    (cab_id,),
                )
                if res.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Cab not found")
            return {"message": "Cab deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:  # pragma: no cover
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    @mcp.tool()
    def update_cab_location(self, cab_id: int, location: CabLocationUpdate) -> Dict[str, str]:
        """Update the cab location"""
        try:
            with get_db() as db:
                cur = db.execute(
                    "SELECT 1 FROM cab_details WHERE cab_model_id=? AND is_deleted=0",
                    (cab_id,),
                )
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Cab not found")

                db.execute(
                    "UPDATE cab_details SET current_lat=?, current_lan=?, updated_date=datetime('now') "
                    "WHERE cab_model_id=? AND is_deleted=0",
                    (location.current_lat, location.current_lan, cab_id),
                )
            return {"message": "Cab location updated successfully"}
        except HTTPException:
            raise
        except Exception as e:  # pragma: no cover
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    @mcp.tool()
    def get_cab_location(self, cab_id: int) -> dict:
        """Fetch cab location"""
        try:
            with get_db() as db:
                cur = db.execute(
                    "SELECT cab_model_id, current_lat, current_lan FROM cab_details "
                    "WHERE cab_model_id=? AND is_deleted=0",
                    (cab_id,),
                )
                row = cur.fetchone()
                if row is None:
                    return {
                        "cab_id": cab_id,
                        "lat": None,
                        "lng": None,
                        "message": "No cab has been assigned for you.",
                    }
                return {
                    "cab_id": int(row["cab_model_id"]),
                    "lat": float(row["current_lat"]) if row["current_lat"] is not None else None,
                    "lng": float(row["current_lan"]) if row["current_lan"] is not None else None,
                }
        except Exception as e:  # pragma: no cover
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

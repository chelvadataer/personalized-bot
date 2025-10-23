import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def auth_headers():
    token = os.getenv("CAB_MCP_TOKEN")
    return {"Authorization": f"Bearer {token}"} if token else {}


def test_add_and_list_cabs():
    # Add a cab
    resp = client.post(
        "/api/cab_details/",
        json={"cab_model_name": "Tesla Model 3", "cab_reg_name": "TN-01-AB-1234"},
        headers=auth_headers(),
    )
    assert resp.status_code in (200, 201)

    # List cabs
    resp2 = client.get("/api/cab_details/", headers=auth_headers())
    assert resp2.status_code == 200
    data = resp2.json()
    assert isinstance(data, list)
    assert any(cab.get("cab_model_name") == "Tesla Model 3" for cab in data)


def test_update_and_get_location():
    # Create cab
    resp = client.post(
        "/api/cab_details/",
        json={"cab_model_name": "Toyota Innova", "cab_reg_name": "KA-05-XY-9999"},
        headers=auth_headers(),
    )
    assert resp.status_code in (200, 201)

    # Find inserted cab id
    list_resp = client.get("/api/cab_details/", headers=auth_headers())
    cab_list = list_resp.json()
    cab = next(c for c in cab_list if c["cab_model_name"] == "Toyota Innova")
    cab_id = cab["cab_model_id"]

    # Update location
    upd = client.put(
        f"/api/cab_details/{cab_id}/location",
        json={"current_lat": 12.9716, "current_lan": 77.5946},
        headers=auth_headers(),
    )
    assert upd.status_code == 200

    # Get location
    loc = client.get(f"/api/cab_details/{cab_id}", headers=auth_headers())
    assert loc.status_code == 200
    data = loc.json()
    assert data["lat"] == 12.9716
    assert data["lng"] == 77.5946

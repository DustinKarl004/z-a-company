def test_admin_can_create_and_list_branches(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = client.post("/branches", json={"name": "Quezon City"}, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Quezon City"
    assert len(body["id"]) == 12

    resp = client.get("/branches", headers=headers)
    assert resp.status_code == 200
    names = [b["name"] for b in resp.json()]
    assert "Quezon City" in names


def test_admin_can_rename_and_delete_branch(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = client.post("/branches", json={"name": "Makati"}, headers=headers)
    branch_id = resp.json()["id"]

    resp = client.patch(f"/branches/{branch_id}", json={"name": "Makati City"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Makati City"

    resp = client.request(
        "DELETE", f"/branches/{branch_id}", json={"password": "adminpass123"}, headers=headers
    )
    assert resp.status_code == 204

    resp = client.get("/branches", headers=headers)
    names = [b["name"] for b in resp.json()]
    assert "Makati City" not in names


def test_cannot_delete_branch_with_staff(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = client.post("/branches", json={"name": "Pasig"}, headers=headers)
    branch_id = resp.json()["id"]

    client.post(
        "/staff",
        json={
            "name": "Jane Dela Cruz",
            "email": "jane@za-company.com",
            "password": "password123",
            "branch_id": branch_id,
        },
        headers=headers,
    )

    resp = client.request(
        "DELETE", f"/branches/{branch_id}", json={"password": "adminpass123"}, headers=headers
    )
    assert resp.status_code == 409

from datetime import date


def test_expenses_admin_only(client, staff_token):
    staff_headers = {"Authorization": f"Bearer {staff_token}"}
    resp = client.get("/expenses", headers=staff_headers)
    assert resp.status_code == 403

    resp = client.post(
        "/expenses",
        json={"branch_id": "whatever", "description": "Ice", "amount": 100},
        headers=staff_headers,
    )
    assert resp.status_code == 403


def test_create_and_list_expense(client, admin_token, branch):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    resp = client.post(
        "/expenses",
        json={"branch_id": branch.id, "description": "Ice", "amount": 150.0},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["branch_id"] == branch.id
    assert body["description"] == "Ice"
    assert body["amount"] == 150.0
    assert body["date"] == date.today().isoformat()

    resp = client.get("/expenses", params={"date": date.today().isoformat()}, headers=admin_headers)
    assert resp.status_code == 200
    listed = resp.json()
    assert len(listed) == 1
    assert listed[0]["id"] == body["id"]


def test_create_expense_requires_branch_id(client, admin_token):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.post(
        "/expenses",
        json={"description": "Ice", "amount": 150.0},
        headers=admin_headers,
    )
    assert resp.status_code == 400


def test_list_expenses_filters_by_branch(client, admin_token, branch, branch2):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    client.post(
        "/expenses",
        json={"branch_id": branch.id, "description": "Ice", "amount": 100.0},
        headers=admin_headers,
    )
    client.post(
        "/expenses",
        json={"branch_id": branch2.id, "description": "Water", "amount": 50.0},
        headers=admin_headers,
    )

    resp = client.get("/expenses", params={"branch_id": branch.id}, headers=admin_headers)
    assert resp.status_code == 200
    listed = resp.json()
    assert len(listed) == 1
    assert listed[0]["description"] == "Ice"


def test_delete_expense(client, admin_token, branch):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.post(
        "/expenses",
        json={"branch_id": branch.id, "description": "Ice", "amount": 100.0},
        headers=admin_headers,
    )
    expense_id = resp.json()["id"]

    resp = client.request(
        "DELETE", f"/expenses/{expense_id}", json={"password": "adminpass123"}, headers=admin_headers
    )
    assert resp.status_code == 204

    resp = client.get("/expenses", headers=admin_headers)
    assert resp.json() == []

    resp = client.request(
        "DELETE", f"/expenses/{expense_id}", json={"password": "adminpass123"}, headers=admin_headers
    )
    assert resp.status_code == 404


def test_delete_expense_requires_correct_password(client, admin_token, branch):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.post(
        "/expenses",
        json={"branch_id": branch.id, "description": "Ice", "amount": 100.0},
        headers=admin_headers,
    )
    expense_id = resp.json()["id"]

    resp = client.request(
        "DELETE", f"/expenses/{expense_id}", json={"password": "wrongpass"}, headers=admin_headers
    )
    assert resp.status_code == 401

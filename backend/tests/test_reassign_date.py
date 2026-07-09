from datetime import date, timedelta


def test_admin_can_reassign_stock_count_date(client, admin_token, branch, stock_item):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.post(
        "/stock-counts",
        json={"branch_id": branch.id, "item_id": stock_item.id, "quantity_remaining": 10},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    count_id = resp.json()["id"]

    new_date = (date.today() - timedelta(days=1)).isoformat()
    resp = client.patch(f"/stock-counts/{count_id}", json={"date": new_date}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["date"] == new_date


def test_staff_cannot_reassign_stock_count_date(client, staff_token, stock_item):
    headers = {"Authorization": f"Bearer {staff_token}"}
    resp = client.post(
        "/stock-counts",
        json={"item_id": stock_item.id, "quantity_remaining": 10},
        headers=headers,
    )
    assert resp.status_code == 201
    count_id = resp.json()["id"]

    new_date = (date.today() - timedelta(days=1)).isoformat()
    resp = client.patch(f"/stock-counts/{count_id}", json={"date": new_date}, headers=headers)
    assert resp.status_code == 403


def test_reassigning_stock_count_date_rejects_conflict(client, admin_token, branch, stock_item):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    client.post(
        "/stock-counts",
        json={"branch_id": branch.id, "item_id": stock_item.id, "date": yesterday, "quantity_remaining": 5},
        headers=admin_headers,
    )
    resp = client.post(
        "/stock-counts",
        json={"branch_id": branch.id, "item_id": stock_item.id, "quantity_remaining": 10},
        headers=admin_headers,
    )
    today_count_id = resp.json()["id"]

    resp = client.patch(f"/stock-counts/{today_count_id}", json={"date": yesterday}, headers=admin_headers)
    assert resp.status_code == 400


def test_admin_can_reassign_stock_delivery_date(client, admin_token, branch, stock_item):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.post(
        "/stock-deliveries",
        json={"branch_id": branch.id, "item_id": stock_item.id, "quantity_delivered": 5},
        headers=admin_headers,
    )
    delivery_id = resp.json()["id"]

    new_date = (date.today() - timedelta(days=1)).isoformat()
    resp = client.patch(f"/stock-deliveries/{delivery_id}", json={"date": new_date}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["date"] == new_date


def test_staff_cannot_reassign_stock_delivery_date(client, staff_token, stock_item):
    headers = {"Authorization": f"Bearer {staff_token}"}
    resp = client.post(
        "/stock-deliveries",
        json={"item_id": stock_item.id, "quantity_delivered": 5},
        headers=headers,
    )
    delivery_id = resp.json()["id"]

    new_date = (date.today() - timedelta(days=1)).isoformat()
    resp = client.patch(f"/stock-deliveries/{delivery_id}", json={"date": new_date}, headers=headers)
    assert resp.status_code == 403


def test_admin_can_reassign_total_sale_date(client, admin_token, branch):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.post(
        "/sales",
        json={"branch_id": branch.id, "amount": 500},
        headers=admin_headers,
    )
    sale_id = resp.json()["id"]

    new_date = (date.today() - timedelta(days=1)).isoformat()
    resp = client.patch(f"/sales/{sale_id}", json={"date": new_date}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["date"] == new_date


def test_reassigning_total_sale_date_rejects_conflict(client, admin_token, branch):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    client.post(
        "/sales",
        json={"branch_id": branch.id, "date": yesterday, "amount": 100},
        headers=admin_headers,
    )
    resp = client.post(
        "/sales",
        json={"branch_id": branch.id, "amount": 200},
        headers=admin_headers,
    )
    today_sale_id = resp.json()["id"]

    resp = client.patch(f"/sales/{today_sale_id}", json={"date": yesterday}, headers=admin_headers)
    assert resp.status_code == 400

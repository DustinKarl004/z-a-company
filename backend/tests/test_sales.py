from datetime import date, timedelta


def test_admin_can_delete_total_sale(client, admin_token, branch):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.post(
        "/sales",
        json={"branch_id": branch.id, "amount": 500.0},
        headers=admin_headers,
    )
    sale_id = resp.json()["id"]

    resp = client.delete(f"/sales/{sale_id}", headers=admin_headers)
    assert resp.status_code == 204

    resp = client.get("/sales", headers=admin_headers)
    assert resp.json() == []

    resp = client.delete(f"/sales/{sale_id}", headers=admin_headers)
    assert resp.status_code == 404


def test_staff_can_delete_own_branch_todays_sale(client, staff_token, stock_item):
    headers = {"Authorization": f"Bearer {staff_token}"}
    resp = client.post(
        "/sales",
        json={"item_id": stock_item.id, "quantity_sold": 5},
        headers=headers,
    )
    sale_id = resp.json()["id"]

    resp = client.delete(f"/sales/{sale_id}", headers=headers)
    assert resp.status_code == 204


def test_staff_cannot_delete_another_branchs_sale(client, admin_token, staff_token, branch2, stock_item):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.post(
        "/sales",
        json={"branch_id": branch2.id, "item_id": stock_item.id, "quantity_sold": 5},
        headers=admin_headers,
    )
    sale_id = resp.json()["id"]

    staff_headers = {"Authorization": f"Bearer {staff_token}"}
    resp = client.delete(f"/sales/{sale_id}", headers=staff_headers)
    assert resp.status_code == 403


def test_staff_cannot_delete_yesterdays_sale(client, admin_token, staff_token, branch, stock_item):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    resp = client.post(
        "/sales",
        json={"branch_id": branch.id, "item_id": stock_item.id, "date": yesterday, "quantity_sold": 5},
        headers=admin_headers,
    )
    sale_id = resp.json()["id"]

    staff_headers = {"Authorization": f"Bearer {staff_token}"}
    resp = client.delete(f"/sales/{sale_id}", headers=staff_headers)
    assert resp.status_code == 403

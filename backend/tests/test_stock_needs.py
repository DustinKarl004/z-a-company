from datetime import date, timedelta


def test_staff_can_flag_and_unflag_a_need(client, staff_token, branch, stock_item):
    headers = {"Authorization": f"Bearer {staff_token}"}
    resp = client.post(
        "/stock-needs",
        json={"item_id": stock_item.id},
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["branch_id"] == branch.id
    assert body["date"] == date.today().isoformat()
    assert body["is_delivered"] is False
    need_id = body["id"]

    resp = client.get("/stock-needs", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = client.delete(f"/stock-needs/{need_id}", headers=headers)
    assert resp.status_code == 204

    resp = client.get("/stock-needs", headers=headers)
    assert resp.json() == []


def test_flagging_the_same_item_twice_is_idempotent(client, staff_token, stock_item):
    headers = {"Authorization": f"Bearer {staff_token}"}
    first = client.post("/stock-needs", json={"item_id": stock_item.id}, headers=headers)
    second = client.post("/stock-needs", json={"item_id": stock_item.id}, headers=headers)
    assert first.json()["id"] == second.json()["id"]

    resp = client.get("/stock-needs", headers=headers)
    assert len(resp.json()) == 1


def test_staff_cannot_flag_a_need_for_another_branch(client, staff_token, branch2, stock_item):
    headers = {"Authorization": f"Bearer {staff_token}"}
    resp = client.post(
        "/stock-needs",
        json={"branch_id": branch2.id, "item_id": stock_item.id},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["branch_id"] != branch2.id


def test_staff_cannot_unflag_yesterdays_need(client, admin_token, staff_token, branch, stock_item):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    resp = client.post(
        "/stock-needs",
        json={"branch_id": branch.id, "item_id": stock_item.id, "date": yesterday},
        headers=admin_headers,
    )
    need_id = resp.json()["id"]

    staff_headers = {"Authorization": f"Bearer {staff_token}"}
    resp = client.delete(f"/stock-needs/{need_id}", headers=staff_headers)
    assert resp.status_code == 403


def test_delivery_staff_can_mark_old_need_delivered(client, admin_token, delivery_token, branch, stock_item):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    resp = client.post(
        "/stock-needs",
        json={"branch_id": branch.id, "item_id": stock_item.id, "date": yesterday},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    need_id = resp.json()["id"]
    assert resp.json()["is_delivered"] is False

    delivery_headers = {"Authorization": f"Bearer {delivery_token}"}
    # marking delivered bypasses the today-only edit restriction
    resp = client.patch(
        f"/stock-needs/{need_id}", json={"is_delivered": True}, headers=delivery_headers
    )
    assert resp.status_code == 200
    assert resp.json()["is_delivered"] is True


def test_staff_cannot_see_another_branchs_needs(client, staff_token, staff_token2, branch2, stock_item):
    headers2 = {"Authorization": f"Bearer {staff_token2}"}
    client.post("/stock-needs", json={"item_id": stock_item.id}, headers=headers2)

    headers1 = {"Authorization": f"Bearer {staff_token}"}
    resp = client.get("/stock-needs", headers=headers1)
    assert resp.status_code == 200
    assert resp.json() == []


def test_all_branch_delivery_staff_must_specify_branch(client, delivery_token, stock_item):
    headers = {"Authorization": f"Bearer {delivery_token}"}
    resp = client.post("/stock-needs", json={"item_id": stock_item.id}, headers=headers)
    assert resp.status_code == 400

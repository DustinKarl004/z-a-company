from datetime import date


def test_today_endpoint_returns_business_date_and_cutoff(client, staff_token):
    headers = {"Authorization": f"Bearer {staff_token}"}
    resp = client.get("/clock/today", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["date"] == date.today().isoformat()
    assert isinstance(body["cutoff_hour"], int)


def test_today_endpoint_requires_auth(client):
    resp = client.get("/clock/today")
    assert resp.status_code == 401

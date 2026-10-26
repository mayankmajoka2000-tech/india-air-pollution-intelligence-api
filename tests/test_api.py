from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health(): assert client.get("/health").status_code==200
def test_india(): assert client.get("/india/states").json()["count"]>=30
def test_emission():
    r=client.post("/emissions/calculate",json={"activity":100,"emission_factor":2,"control_efficiency":.25})
    assert r.json()["net"]==150


def test_root_serves_landing_page_to_browsers():
    from fastapi.testclient import TestClient
    from app.main import app
    c = TestClient(app)
    r = c.get("/", headers={"accept": "text/html,application/xhtml+xml"})
    assert r.status_code == 200 and "India's air" in r.text and 'href="/docs"' in r.text
    j = c.get("/", headers={"accept": "application/json"})
    assert j.status_code == 200 and j.json()["status"] == "operational"

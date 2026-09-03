from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health(): assert client.get("/health").status_code==200
def test_india(): assert client.get("/india/states").json()["count"]>=30
def test_emission():
    r=client.post("/emissions/calculate",json={"activity":100,"emission_factor":2,"control_efficiency":.25})
    assert r.json()["net"]==150

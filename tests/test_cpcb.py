"""Tests for the CPCB AQI engine and the live data.gov.in integration (mocked)."""
import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import cpcb_client as cpcb
from app.services.cpcb_aqi import calculate_cpcb_aqi, category, sub_index

client = TestClient(app)


# ------------------------------------------------------------ AQI engine
@pytest.mark.parametrize("pollutant,conc,expected", [
    ("PM2.5", 0, 0), ("PM2.5", 30, 50), ("PM2.5", 60, 100), ("PM2.5", 90, 200),
    ("PM2.5", 120, 300), ("PM2.5", 250, 400), ("PM2.5", 80, 166),
    ("PM10", 100, 100), ("PM10", 250, 200), ("PM10", 140, 127),
    ("NO2", 80, 100), ("CO", 2.0, 100), ("CO", 10, 200), ("O3", 168, 200),
    ("SO2", 380, 200), ("NH3", 400, 100), ("Pb", 1.0, 100),
])
def test_sub_index_breakpoints(pollutant, conc, expected):
    assert sub_index(pollutant, conc) == expected


def test_severe_capped_at_500():
    assert sub_index("PM2.5", 5000) == 500


def test_categories():
    assert category(50) == "Good" and category(51) == "Satisfactory"
    assert category(201) == "Poor" and category(450) == "Severe"


def test_minimum_data_rule():
    assert calculate_cpcb_aqi({"no2": 50, "so2": 20, "co": 1})["valid"] is False
    assert calculate_cpcb_aqi({"pm25": 80, "no2": 50})["valid"] is False
    r = calculate_cpcb_aqi({"pm25": 80, "pm10": 140, "no2": 50})
    assert r["valid"] and r["aqi"] == 166 and r["prominent_pollutant"] == "PM2.5"


def test_aqi_endpoint():
    r = client.post("/aqi/calculate", json={"pm25": 95, "pm10": 180, "no2": 70})
    body = r.json()
    assert r.status_code == 200 and body["aqi"] == 215 and body["category"] == "Poor"


def test_breakpoints_endpoint():
    assert "PM2.5" in client.get("/aqi/breakpoints").json()


# ------------------------------------------------------------ live feed (mocked)
FEED = {
    "status": "ok", "total": 7, "count": 7,
    "records": [
        {"country": "India", "state": "Haryana", "city": "Faridabad",
         "station": "Sector 11, Faridabad - HSPCB", "last_update": "21-10-2026 15:00:00",
         "latitude": "28.37", "longitude": "77.31", "pollutant_id": "PM2.5",
         "min_value": "120", "max_value": "310", "avg_value": "236"},
        {"country": "India", "state": "Haryana", "city": "Faridabad",
         "station": "Sector 11, Faridabad - HSPCB", "last_update": "21-10-2026 15:00:00",
         "latitude": "28.37", "longitude": "77.31", "pollutant_id": "PM10",
         "min_value": "90", "max_value": "260", "avg_value": "184"},
        {"country": "India", "state": "Haryana", "city": "Faridabad",
         "station": "Sector 11, Faridabad - HSPCB", "last_update": "21-10-2026 15:00:00",
         "latitude": "28.37", "longitude": "77.31", "pollutant_id": "OZONE",
         "min_value": "4", "max_value": "60", "avg_value": "22"},
        # old schema field names
        {"country": "India", "state": "Delhi", "city": "Delhi",
         "station": "Anand Vihar, Delhi - DPCC", "last_update": "21-10-2026 15:00:00",
         "pollutant_id": "PM2.5", "pollutant_min": "200", "pollutant_max": "400",
         "pollutant_avg": "312", "pollutant_unit": "NA"},
        {"country": "India", "state": "Delhi", "city": "Delhi",
         "station": "Anand Vihar, Delhi - DPCC", "last_update": "21-10-2026 15:00:00",
         "pollutant_id": "NO2", "pollutant_min": "20", "pollutant_max": "90",
         "pollutant_avg": "55", "pollutant_unit": "NA"},
        {"country": "India", "state": "Delhi", "city": "Delhi",
         "station": "Anand Vihar, Delhi - DPCC", "last_update": "21-10-2026 15:00:00",
         "pollutant_id": "CO", "pollutant_min": "10", "pollutant_max": "80",
         "pollutant_avg": "NA", "pollutant_unit": "NA"},
        {"country": "India", "state": "Delhi", "city": "Delhi",
         "station": "Anand Vihar, Delhi - DPCC", "last_update": "21-10-2026 15:00:00",
         "pollutant_id": "SO2", "pollutant_min": "5", "pollutant_max": "20",
         "pollutant_avg": "12", "pollutant_unit": "NA"},
    ],
}


@pytest.fixture
def mocked_feed(monkeypatch):
    calls = []

    def handler(request: httpx.Request):
        calls.append(request)
        return httpx.Response(200, json=FEED)

    monkeypatch.setattr(cpcb, "client", cpcb.CPCBClient(transport=httpx.MockTransport(handler)))
    monkeypatch.setenv("DATA_GOV_IN_API_KEY", "test-key")
    return calls


def test_normalise_both_schemas():
    new = cpcb.normalise_record(FEED["records"][0])
    old = cpcb.normalise_record(FEED["records"][3])
    assert new["avg"] == 236 and new["latitude"] == 28.37
    assert old["avg"] == 312 and old["pollutant"] == "PM2.5"
    assert new["last_update"] == "2026-10-21T15:00:00+05:30"
    assert cpcb.normalise_record({"pollutant_id": "XYZ"}) is None


def test_live_stations(mocked_feed):
    r = client.get("/live/stations")
    assert r.status_code == 200
    body = r.json()
    assert body["source"]["resource_id"] == cpcb.RESOURCE_ID
    st = {s["station"]: s for s in body["stations"]}
    assert st["Anand Vihar, Delhi - DPCC"]["aqi"] == 312
    assert st["Anand Vihar, Delhi - DPCC"]["category"] == "Very Poor"
    assert st["Sector 11, Faridabad - HSPCB"]["aqi"] == 236
    assert body["stations"][0]["aqi"] >= body["stations"][1]["aqi"]
    assert mocked_feed[0].url.params["api-key"] == "test-key"


def test_live_filters_and_cache(mocked_feed):
    client.get("/live/cities", params={"state": "Tamil Nadu"})
    client.get("/live/cities", params={"state": "Tamil Nadu"})
    assert len(mocked_feed) == 1
    assert mocked_feed[0].url.params["filters[state]"] == "Tamil_Nadu"


def test_live_readings_pollutant_filter(mocked_feed):
    body = client.get("/live/readings", params={"pollutant": "ozone"}).json()
    assert body["count"] == 1 and body["readings"][0]["pollutant"] == "O3"


def test_live_unavailable(monkeypatch, tmp_path):
    monkeypatch.setattr(cpcb, "SNAPSHOT_PATH", tmp_path / "none.json")

    def handler(request):
        return httpx.Response(502)
    monkeypatch.setattr(cpcb, "client", cpcb.CPCBClient(transport=httpx.MockTransport(handler)))
    r = client.get("/live/stations")
    assert r.status_code == 503 and "unavailable" in r.json()["detail"]["error"]


def test_concentration_mode(mocked_feed, monkeypatch):
    monkeypatch.setenv("CPCB_FEED_VALUES", "concentration")
    st = {s["station"]: s for s in client.get("/live/stations").json()["stations"]}
    # PM2.5 236 ug/m3 -> 389 via breakpoints
    assert st["Sector 11, Faridabad - HSPCB"]["aqi"] == sub_index("PM2.5", 236)


def test_snapshot_fallback(monkeypatch, tmp_path):
    snap = tmp_path / "snap.json"
    snap.write_text(__import__("json").dumps({"fetched_at": "2026-10-22T16:00:00+00:00",
                                               "feed_updated": "2026-10-22T16:02:50Z", "total": 7,
                                               "records": FEED["records"]}))
    monkeypatch.setattr(cpcb, "SNAPSHOT_PATH", snap)

    def handler(request):
        raise httpx.ConnectError("No route to host")
    monkeypatch.setattr(cpcb, "client", cpcb.CPCBClient(transport=httpx.MockTransport(handler)))
    r = client.get("/live/stations")
    assert r.status_code == 200
    b = r.json()
    assert b["mode"] == "snapshot" and b["snapshot_as_of"] == "2026-10-22T16:02:50Z"
    assert {s["station"] for s in b["stations"]} == {"Sector 11, Faridabad - HSPCB", "Anand Vihar, Delhi - DPCC"}
    assert client.get("/live/status").json()["status"] == "snapshot"
    d = client.get("/live/stations", params={"state": "Delhi"}).json()
    assert d["count"] == 1


def test_no_snapshot_still_503(monkeypatch, tmp_path):
    monkeypatch.setattr(cpcb, "SNAPSHOT_PATH", tmp_path / "missing.json")

    def handler(request):
        raise httpx.ConnectError("No route to host")
    monkeypatch.setattr(cpcb, "client", cpcb.CPCBClient(transport=httpx.MockTransport(handler)))
    assert client.get("/live/stations").status_code == 503

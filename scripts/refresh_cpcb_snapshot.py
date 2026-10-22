"""
Refresh data/cpcb_snapshot.json from the CPCB real-time feed on data.gov.in.

data.gov.in only answers requests from inside India, so run this on a machine in India:

    DATA_GOV_IN_API_KEY=your_key python scripts/refresh_cpcb_snapshot.py
    # or, from the CSV downloaded on the data.gov.in resource page (no key needed):
    python scripts/refresh_cpcb_snapshot.py --from-csv path/to/downloaded.csv
    git add data/cpcb_snapshot.json && git commit -m "Refresh CPCB snapshot" && git push

The hosted API serves this file whenever it cannot reach the live feed.
"""
import csv
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RESOURCE = "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
OUT = Path(__file__).resolve().parents[1] / "data" / "cpcb_snapshot.json"


def from_csv(path: str) -> None:
    with open(path, newline="", encoding="utf-8-sig") as f:
        records = [{k.strip().lower(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]
    times = sorted(r.get("last_update", "") for r in records if r.get("last_update"))
    OUT.write_text(json.dumps({"resource_id": RESOURCE, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                               "feed_updated": times[-1] if times else None, "total": len(records),
                               "source_file": Path(path).name, "records": records}, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(records)} readings from {path} to {OUT}")


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "--from-csv":
        return from_csv(sys.argv[2])
    key = os.getenv("DATA_GOV_IN_API_KEY")
    if not key:
        sys.exit("Set DATA_GOV_IN_API_KEY (free key from data.gov.in → My Account → Generate Key)")
    records, offset, total, updated = [], 0, None, None
    while total is None or offset < total:
        q = urllib.parse.urlencode({"api-key": key, "format": "json", "limit": 1000, "offset": offset})
        with urllib.request.urlopen(f"https://api.data.gov.in/resource/{RESOURCE}?{q}", timeout=60) as r:
            page = json.load(r)
        if page.get("status") == "error" or "records" not in page:
            sys.exit(f"data.gov.in error: {page}")
        total, updated = int(page.get("total", 0)), page.get("updated_date")
        records += page["records"]
        if not page["records"]:
            break
        offset += 1000
    OUT.write_text(json.dumps({"resource_id": RESOURCE, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                               "feed_updated": updated, "total": total, "records": records}, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(records)} of {total} readings (feed updated {updated}) to {OUT}")


if __name__ == "__main__":
    main()

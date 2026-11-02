"""Download the Space-Track GP history used in the analysis.

Credentials are read from the environment variables SPACETRACK_USER and
SPACETRACK_PASSWORD. The file is written to data/tle_gp_history_59103_68762.csv,
which is the path read by the notebook.

Usage (from the repository root):
    export SPACETRACK_USER="your_email"
    export SPACETRACK_PASSWORD="your_password"
    python src/download_data.py

By default only element sets created before the original download
(2026-10-27 10:15 UTC) are requested, so that the dataset matches the one used
in the article (1408 records). Use --created-before none to fetch everything
currently available.
"""
import argparse
import os
import sys
from pathlib import Path
from urllib.parse import quote

import requests

BASE_URL = "https://www.space-track.org"
LOGIN_URL = f"{BASE_URL}/ajaxauth/login"
LOGOUT_URL = f"{BASE_URL}/ajaxauth/logout"

NORAD_IDS = [59103, 68762]          # ICEYE-X36, Cosmos 2612
EPOCH_START = "2026-04-01"
EPOCH_END = "2026-10-28"
CREATED_BEFORE = "2026-10-27 10:15:00"
EXPECTED_RECORDS = 1408

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "data" / "tle_gp_history_59103_68762.csv"


def build_query(created_before):
    parts = [
        "basicspacedata", "query", "class", "gp_history",
        "NORAD_CAT_ID", ",".join(str(n) for n in NORAD_IDS),
        "EPOCH", f"{EPOCH_START}--{EPOCH_END}",
    ]
    if created_before:
        parts += ["CREATION_DATE", "<" + created_before]
    parts += ["orderby", "NORAD_CAT_ID,EPOCH", "format", "csv"]
    return BASE_URL + "/" + "/".join(quote(p, safe=",-:") for p in parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--created-before", default=CREATED_BEFORE,
                        help="only element sets created before this UTC date/time; 'none' disables the filter")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    user = os.environ.get("SPACETRACK_USER")
    password = os.environ.get("SPACETRACK_PASSWORD")
    if not user or not password:
        sys.exit("Set SPACETRACK_USER and SPACETRACK_PASSWORD (free account at https://www.space-track.org).")

    created_before = None if args.created_before.lower() == "none" else args.created_before
    url = build_query(created_before)

    with requests.Session() as s:
        r = s.post(LOGIN_URL, data={"identity": user, "password": password}, timeout=60)
        if r.status_code != 200 or "Failed" in r.text:
            sys.exit(f"Space-Track login failed (HTTP {r.status_code}).")
        print(f"Requesting {url}")
        r = s.get(url, timeout=300)
        s.get(LOGOUT_URL, timeout=60)
    r.raise_for_status()

    text = r.text
    if not text.startswith("CCSDS_OMM_VERS"):
        sys.exit("Unexpected response from Space-Track:\n" + text[:500])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    n = max(len(text.strip().splitlines()) - 1, 0)
    print(f"Saved {n} records to {args.output}")
    if created_before == CREATED_BEFORE and n != EXPECTED_RECORDS:
        print(f"Warning: the article used {EXPECTED_RECORDS} records; results may differ slightly.")


if __name__ == "__main__":
    main()

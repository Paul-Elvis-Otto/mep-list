# mep_download/eu_api.py

import os
import csv
import json
import time
import argparse
import requests
from tqdm import tqdm

API_BASE = "https://data.europarl.europa.eu/api/v2/meps"

# Rate limit configuration
REQUESTS_PER_MINUTE = 100
MIN_INTERVAL = 60.0 / REQUESTS_PER_MINUTE  # seconds between requests


def fetch_mep(mep_id: str, out_dir: str, user_agent: str) -> None:
    """
    Fetch a single MEP record by ID and save it as JSON.
    """
    url = f"{API_BASE}/{mep_id}"
    headers = {
        "Accept": "application/ld+json",
        "User-Agent": user_agent
    }
    params = {"format": "application/ld+json"}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()

    out_path = os.path.join(out_dir, f"{mep_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(resp.json(), f, indent=2, ensure_ascii=False)


def fetch_all(
    csv_path: str,
    out_dir: str,
    id_column: str,
    user_agent: str,
    skip_existing: bool = True
) -> None:
    """
    Read the CSV at `csv_path`, extract all IDs in `id_column`, and
    fetch each MEP via the EP API, saving one JSON file per MEP into `out_dir`.
    Shows a tqdm progress bar, with rate limiting of 100 requests/minute.
    """
    os.makedirs(out_dir, exist_ok=True)

    # load all rows so we know total for tqdm
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = list(csv.DictReader(csvfile))

    for row in tqdm(reader, desc="Fetching MEPs", unit="mep"):
        mep_id = row.get(id_column)
        if not mep_id:
            continue

        json_path = os.path.join(out_dir, f"{mep_id}.json")
        if skip_existing and os.path.exists(json_path):
            tqdm.write(f"Skipping {mep_id}, file exists.")
            continue

        start = time.time()
        try:
            fetch_mep(mep_id, out_dir, user_agent)
            tqdm.write(f"Saved {mep_id} → {json_path}")
        except Exception as e:
            tqdm.write(f"Error fetching {mep_id}: {e}")

        # enforce rate limit
        elapsed = time.time() - start
        if elapsed < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - elapsed)


def main():
    p = argparse.ArgumentParser(
        description="Fetch one JSON per MEP ID from the EP API with progress bar."
    )
    p.add_argument(
        "--csv", default="./input_data/members.csv",
        help="Path to the decompressed members CSV"
    )
    p.add_argument(
        "--outdir", default="./input_data",
        help="Directory to write {mep_id}.json files into"
    )
    p.add_argument(
        "--id-column", default="id",
        help="CSV column name containing the numeric MEP ID"
    )
    p.add_argument(
        "--user-agent", default="user1-prd-1.0.0",
        help="User-Agent header for the API requests"
    )
    p.add_argument(
        "--no-skip", action="store_false", dest="skip_existing",
        help="Re-fetch even if output file already exists"
    )

    args = p.parse_args()
    fetch_all(
        csv_path=args.csv,
        out_dir=args.outdir,
        id_column=args.id_column,
        user_agent=args.user_agent,
        skip_existing=args.skip_existing
    )


if __name__ == "__main__":
    main()

# mep_list/wrangle.py

import os
import json
import pandas as pd


def _clean_uri(uri: str) -> str:
    """
    Turn a URI like
      http://…/human-sex/FEMALE
    into just "FEMALE".
    """
    if not uri or not isinstance(uri, str):
        return ""
    return uri.rstrip("/").split("/")[-1]


def wrangle(csv_path: str, json_dir: str, output_dir: str) -> pd.DataFrame:
    """
    1) Load the CSV at csv_path (expects a column 'id' as str).
    2) For each row, open json_dir/{id}.json,
       pull out selected fields, clean URIs, collect into a DataFrame.
    3) Merge on 'id', write out to
       output_dir/members_enriched.csv and return the DataFrame.

    Returns:
      pd.DataFrame  -- the merged/enriched dataframe
    """
    # 1) read the base CSV, treating 'id' as string
    df = pd.read_csv(csv_path, dtype={"id": str})

    # 2) define which JSON fields to keep
    keep_fields = [
        "bday",
        "hasGender",
        "hasHonorificPrefix",
        "citizenship",
        "placeOfBirth",
        "img",
    ]

    # 3) build a list of per-MEP dicts
    records = []
    for _, row in df.iterrows():
        mep_id = row["id"]
        json_path = os.path.join(json_dir, f"{mep_id}.json")
        if not os.path.isfile(json_path):
            continue

        with open(json_path, encoding="utf-8") as f:
            payload = json.load(f).get("data", [])
        if not payload:
            continue

        person = payload[0]
        rec = {"id": mep_id}
        for field in keep_fields:
            val = person.get(field, "")
            # clean URIs for these three fields
            if field in ("hasGender", "hasHonorificPrefix", "citizenship"):
                val = _clean_uri(val)
            rec[field] = val

        records.append(rec)

    # 4) turn into a DataFrame and merge
    df_json = pd.DataFrame(records)
    df_out = df.merge(df_json, on="id", how="left")

    # 5) write out for debugging
    os.makedirs(output_dir, exist_ok=True)
    out_csv = os.path.join(output_dir, "members_enriched.csv")
    df_out.to_csv(out_csv, index=False)

    return df_out

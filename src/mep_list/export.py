import os
import pandas as pd


def export_data(
    df: pd.DataFrame,
    export_dir: str,
    base_name: str = "members_enriched"
) -> None:
    """
    Export a DataFrame to multiple formats in export_dir.

    :param df: DataFrame to export
    :param export_dir: directory to write files into
    :param base_name: base filename (without extension)
    """
    os.makedirs(export_dir, exist_ok=True)

    # CSV
    csv_path = os.path.join(export_dir, f"{base_name}.csv")
    df.to_csv(csv_path, index=False)

    # JSON (records orient)
    json_path = os.path.join(export_dir, f"{base_name}.json")
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    # TSV
    tsv_path = os.path.join(export_dir, f"{base_name}.tsv")
    df.to_csv(tsv_path, sep="\t", index=False)

    # Excel
    xlsx_path = os.path.join(export_dir, f"{base_name}.xlsx")
    df.to_excel(xlsx_path, index=False)

    # Parquet (optional)
    try:
        parquet_path = os.path.join(export_dir, f"{base_name}.parquet")
        df.to_parquet(parquet_path, index=False)
    except (ImportError, ValueError):
        parquet_path = None

    print(f"✔ Exported data to {export_dir}:")
    print(f"  - {os.path.basename(csv_path)}")
    print(f"  - {os.path.basename(json_path)}")
    print(f"  - {os.path.basename(tsv_path)}")
    print(f"  - {os.path.basename(xlsx_path)}")
    if parquet_path and os.path.exists(parquet_path):
        print(f"  - {os.path.basename(parquet_path)}")

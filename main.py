from mep_download import download_and_decompress
from mep_download.eu_api import fetch_all
from mep_download.scrape_socials import scrape_social_media
from mep_list.wrangle import wrangle
from mep_list.export import export_data

def main():
    # 1) Download & decompress the members.csv.gz
    url = (
        "https://github.com/HowTheyVote/data/releases/download/"
        "2025-07-07/members.csv.gz"
    )
    input_dir = "./input_data"
    csv_path = download_and_decompress(url, input_dir)
    print(f"✔ Downloaded and decompressed CSV to: {csv_path}")

    # 2) Fetch individual MEP JSONs
    fetch_all(
        csv_path=csv_path,
        out_dir=input_dir,
        id_column="id",
        user_agent="user1-prd-1.0.0",
        skip_existing=True,
    )
    print(f"✔ Fetched individual MEP JSONs into: {input_dir}/")

    # 3) Enrich CSV with JSON fields
    debug_dir = "./data_tmp"
    df_enriched = wrangle(
        csv_path=csv_path,
        json_dir=input_dir,
        output_dir=debug_dir
    )
    print(f"✔ Enriched CSV written to: {debug_dir}/members_enriched.csv")

    # 4) Scrape social media and add 'social_media' column
    scraper_ua = (
        "Mozilla/5.0 (compatible; MEP-Scraper/1.0;"
        " +https://github.com/YourRepo)"
    )
    df_with_social = scrape_social_media(df_enriched, user_agent=scraper_ua)
    print("✔ Scraped social media profiles for all MEPs")

    # 5) Export final DataFrame to multiple formats
    export_dir = "./export_data"
    export_data(
        df=df_with_social,
        export_dir=export_dir,
        base_name="members_enriched"
    )
    print(f"✔ Exported enriched data to: {export_dir}/")

if __name__ == "__main__":
    main()

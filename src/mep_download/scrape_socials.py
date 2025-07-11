import json
import os
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# rate‐limit: 20 requests per minute
REQUESTS_PER_MINUTE = 20
MIN_INTERVAL = 60.0 / REQUESTS_PER_MINUTE

# URL template for each MEP's page
URL_TMPL = "https://www.europarl.europa.eu/meps/en/{}"
CACHE_FILE = "data_tmp/social_media_cache.json"


def load_cache() -> dict:
    """Load cache from file if it exists."""
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_cache(cache: dict):
    """Save cache to file."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def scrape_social_media(
    df: pd.DataFrame,
    user_agent: str,
) -> pd.DataFrame:
    """
    Scrape social‐media links for each MEP in `df` (expects an 'id' column).
    Returns a new DataFrame with a 'social_media' column containing dicts.
    """
    headers = {"User-Agent": user_agent}
    results = []
    cache = load_cache()

    for _, row in tqdm(df.iterrows(),
                       total=len(df),
                       desc="Scraping social media",
                       unit="mep"):
        mep_id = str(row["id"])

        if mep_id in cache:
            tqdm.write(f"{mep_id}: found in cache, skipping scrape")
            results.append(cache[mep_id])
            continue

        url = URL_TMPL.format(mep_id)
        start = time.time()
        profiles = {}

        try:
            resp = requests.get(url, headers=headers, allow_redirects=True)
            if resp.status_code == 404:
                tqdm.write(f"{mep_id}: page not found (404), skipping")
            else:
                resp.raise_for_status()

                soup = BeautifulSoup(resp.text, "html.parser")

                # Debug: Check if the container exists
                container = soup.select_one(".erpl_social-share-horizontal")
                if not container:
                    tqdm.write(f"{mep_id}: social media container not found")
                    # Try alternative selectors for debugging
                    alt_containers = soup.select(
                        ".erpl_social-share-horizontal")
                    tqdm.write(
                        f"{mep_id}: found {len(alt_containers)} containers with class"
                    )

                    # Check if there are any social links at all
                    all_social_links = soup.find_all(
                        "a",
                        class_=lambda x: x and any(
                            c.startswith("link_") for c in x))
                    tqdm.write(
                        f"{mep_id}: found {len(all_social_links)} total social links"
                    )
                else:
                    # Find all social media links in the container
                    social_links = container.find_all("a", href=True)
                    tqdm.write(
                        f"{mep_id}: found {len(social_links)} links in container"
                    )

                    for a in social_links:
                        href = a["href"].strip()
                        if not href:
                            continue

                        # derive platform name from class (e.g. link_fb → fb)
                        cls = a.get("class", [])
                        platform = None
                        for c in cls:
                            if c.startswith("link_"):
                                platform = c.split("_", 1)[1]
                                break

                        if not platform:
                            # fallback to screen‐reader text
                            sr = a.find("span", class_="sr-only")
                            platform = sr.text.strip().lower() if sr else "unknown"

                        profiles[platform] = href
                        tqdm.write(f"{mep_id}: found {platform} -> {href}")

            tqdm.write(f"{mep_id}: total profiles found: {len(profiles)}")
            cache[mep_id] = profiles
            save_cache(cache)
        except Exception as e:
            tqdm.write(f"Error scraping {mep_id}: {e}")
            # NOTE: we don't cache errors, so they can be retried
        finally:
            # enforce rate limit
            elapsed = time.time() - start
            if elapsed < MIN_INTERVAL:
                time.sleep(MIN_INTERVAL - elapsed)

        results.append(profiles)

    df_out = df.copy()
    df_out["social_media"] = results
    return df_out

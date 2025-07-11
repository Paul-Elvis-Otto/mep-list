import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

# rate‐limit: 20 requests per minute
REQUESTS_PER_MINUTE = 20
MIN_INTERVAL = 60.0 / REQUESTS_PER_MINUTE

# URL template for each MEP's page
URL_TMPL = "https://www.europarl.europa.eu/meps/en/{}"


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

    for _, row in tqdm(df.iterrows(),
                       total=len(df),
                       desc="Scraping social media",
                       unit="mep"):
        mep_id = str(row["id"])
        url = URL_TMPL.format(mep_id)
        start = time.time()
        profiles = {}

        try:
            resp = requests.get(url, headers=headers, allow_redirects=True)
            if resp.status_code == 404:
                tqdm.write(f"{mep_id}: page not found (404), skipping")
                results.append(profiles)
                continue
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Debug: Check if the container exists
            container = soup.select_one(".erpl_social-share-horizontal")
            if not container:
                tqdm.write(f"{mep_id}: social media container not found")
                # Try alternative selectors for debugging
                alt_containers = soup.select(".erpl_social-share-horizontal")
                tqdm.write(f"{mep_id}: found {len(alt_containers)} containers with class")
                
                # Check if there are any social links at all
                all_social_links = soup.find_all("a", class_=lambda x: x and any(c.startswith("link_") for c in x))
                tqdm.write(f"{mep_id}: found {len(all_social_links)} total social links")
                
                results.append(profiles)
                continue
            
            # Find all social media links in the container
            social_links = container.find_all("a", href=True)
            tqdm.write(f"{mep_id}: found {len(social_links)} links in container")
            
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
        except Exception as e:
            tqdm.write(f"Error scraping {mep_id}: {e}")
        finally:
            # enforce rate limit
            elapsed = time.time() - start
            if elapsed < MIN_INTERVAL:
                time.sleep(MIN_INTERVAL - elapsed)

        results.append(profiles)

    df_out = df.copy()
    df_out["social_media"] = results
    return df_out

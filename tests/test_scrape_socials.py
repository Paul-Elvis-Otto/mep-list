# tests/test_scrape_socials.py

import pandas as pd
import pytest
from mep_download.scrape_socials import scrape_social_media

@pytest.mark.integration
def test_scrape_social_media_real_ids():
    """
    Integration test: for a small set of real MEP IDs, scrape their
    social media profiles from the live EP website and assert that
    the output DataFrame has a 'social_media' dict column with valid URLs.
    """
    # These MEP IDs should correspond to real profiles on europarl.europa.eu
    ids = [
        1909,  # Keep this one
        1927,  # Try another ID
    ]
    # Build DataFrame
    df = pd.DataFrame({"id": [str(i) for i in ids]})

    # Use a realistic User-Agent
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )

    # Run the scraper
    df_out = scrape_social_media(df, user_agent=user_agent)

    # Create output DataFrame with renamed column
    output_df = df_out[['id', 'social_media']].copy()
    output_df = output_df.rename(columns={'social_media': 'socials'})
    
    # Save to CSV
    csv_filename = "test_social_media_output.csv"
    output_df.to_csv(csv_filename, index=False)
    
    # Print confirmation and preview
    print(f"\n" + "="*60)
    print(f"CSV saved as: {csv_filename}")
    print("="*60)
    print("DataFrame preview:")
    print(output_df.to_string())
    
    print("\n" + "-"*60)
    print("DETAILED SOCIAL MEDIA PROFILES:")
    print("-"*60)
    for _, row in output_df.iterrows():
        mep_id = row['id']
        profiles = row['socials']
        print(f"\nMEP {mep_id}:")
        if profiles:
            for platform, url in profiles.items():
                print(f"  {platform}: {url}")
        else:
            print("  No social media profiles found")
    print("="*60)

    # Sanity checks
    assert "socials" in output_df.columns
    assert len(output_df) == len(df)

    # Each entry must be a dict; URLs must look valid if present
    any_profiles = False
    for _, row in output_df.iterrows():
        sm = row["socials"]
        assert isinstance(sm, dict)
        for platform, url in sm.items():
            # platform is non-empty string
            assert isinstance(platform, str) and platform
            # url should be a valid URL (http/https) or email (including obfuscated)
            assert isinstance(url, str) and (
                url.startswith("http") or 
                url.startswith("mailto:") or
                "@" in url or  # Regular email
                "[at]" in url  # Obfuscated email
            )
        if sm:
            any_profiles = True

    # Ensure at least one of the test IDs has a social media profile
    assert any_profiles, "Expected at least one profile but found none"

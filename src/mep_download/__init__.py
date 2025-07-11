# member_downloader/__init__.py

"""
member_downloader

Provides functionality to download and decompress
a gzipped CSV file into a local directory.
"""
from .how_they_vote_members import download_and_decompress
from .eu_api import fetch_all
from .scrape_socials import *

__all__ = ["download_and_decompress", "fetch_all"]

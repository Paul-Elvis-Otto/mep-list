# member_downloader/downloader.py

import os
import gzip
import shutil
import requests


def download_and_decompress(
    url: str, output_dir: str, remove_gzip: bool = True
) -> str:
    """
    Download a .gz file from `url`, decompress it, and save the
    resulting CSV into `output_dir`. Returns the path to the CSV.

    :param url: direct link to a .gz file
    :param output_dir: local directory to hold the output
    :param remove_gzip: if True, delete the .gz after decompression
    :return: path to decompressed CSV file
    """
    os.makedirs(output_dir, exist_ok=True)

    # derive filenames
    gz_filename = os.path.basename(url)
    gz_path = os.path.join(output_dir, gz_filename)
    csv_filename = gz_filename.rstrip(".gz")
    csv_path = os.path.join(output_dir, csv_filename)

    # download with streaming
    with requests.get(url, stream=True) as resp:
        resp.raise_for_status()
        with open(gz_path, "wb") as out_f:
            for chunk in resp.iter_content(chunk_size=8192):
                out_f.write(chunk)

    # decompress
    with gzip.open(gz_path, "rb") as f_in, open(csv_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    # optionally clean up
    if remove_gzip:
        os.remove(gz_path)

    return csv_path

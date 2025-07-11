# MEP List

```diff
! This is currently under heavy construction !
! expect breaking changes !
```

This project provides a comprehensive and enriched dataset of Members of the European Parliament (MEPs). It aggregates data from various sources, including the official European Parliament API, [HowTheyVote.eu](https://howtheyvote.eu/), and custom scraping for social media profiles, to create a unified and easy-to-use dataset.

The primary goal is to simplify the process of working with MEP data for researchers, journalists, and developers.

## Features

- **Data Aggregation**: Combines data from a base CSV with detailed information from the EU Parliament's API.
- **Data Enrichment**: Adds social media profiles (e.g., Twitter, Facebook, Instagram) for each MEP by scraping their official pages.
- **Multiple Export Formats**: Exports the final, enriched dataset into CSV, JSON, TSV, and Excel (.xlsx) formats.
- **Efficient Setup**: Uses `uv` for fast and straightforward dependency management.
- **Modular Structure**: The code is organized into distinct modules for downloading, wrangling, and exporting data.

## Installation & Usage

This project uses `uv` for package and environment management.

### Prerequisites

- Python 3.11 or higher.
- `uv` installed. You can install it with `pip install uv`.

### Quickstart

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd mep-list
    ```

2. **Create a virtual environment and install dependencies:**

    ```bash
    uv sync 
    ```

    *(Note: Based on `pyproject.toml`, you might need to generate a `requirements.txt` first or install dependencies directly. If a `requirements.txt` is not present, you can use `uv pip install .`)*

3. **Run the main pipeline:**
    This single command will execute the entire data aggregation and enrichment process.

    ```bash
    uv run main.py
    ```

Upon successful execution, the final datasets will be available in the `./export_data/` directory.

## Project Structure

- `main.py`: The main script that orchestrates the entire data processing pipeline.
- `input_data/`: Stores the raw data downloaded from various sources, including the initial CSV and individual MEP JSON files.
- `data_tmp/`: A temporary directory for intermediate data files, such as the enriched CSV before social media scraping.
- `export_data/`: The output directory where the final, enriched datasets are saved in various formats.
- `src/`: Contains the source code for the project, likely organized into sub-packages like `mep_download` and `mep_list`.
- `pyproject.toml`: The project definition file, containing metadata and dependencies.

## Data Sources

- **Base Data**: `members.csv.gz` from [HowTheyVote/data](https://github.com/HowTheyVote/data) GitHub releases.
- **MEP Details**: Official [European Parliament API](https://data.europarl.europa.eu/elections/Meps/get).
- **Social Media**: Scraped from the official MEP profile pages on the European Parliament website.

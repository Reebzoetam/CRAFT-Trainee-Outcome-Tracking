# CRAFT-Trainee-Outcome-Tracking

## Introduction
This is a Python-based data pipeline designed to track and analyze research outcomes for researchers and authors of publications. This tool was developed as part of a 2025-2026 work-study project to support program evaluation for the Centre for Research and Applications in Fluidic Technologies (CRAFT). It enables efficient, reproducible tracking of trainee research impact and academic progression.

Using the OpenAlex API, the script retrieves publication data for a list of researchers (via ORCID IDs or OpenAlex author IDs) and computes key academic metrics, including:

- Total number of publications
- Total citation count
- h-index
- Most cited works
- Journal publication distribution
- Institutional affiliations across publications

## Features

- Automatic author lookup from ORCID or OpenAlex author IDs
- Optional date-range filtering
- Full publication metadata extraction (title, authors, journal, issue, date)
- Citation analysis and h-index computation
- Institution tracking
- Dual CSV export:
    - Curated dataset (summary metrics per researcher)
    - Raw dataset (detailed publication-level data)

Please see the [outputs](/final_scripts/data_manipulation.py) folder for sample .csv outputs.

## How to Run

The script can be run directly in a code editor. 

Make sure you have Python 3 installed, then run:

```bash
python3 -m pip install requests
```

Ensure that you have the requests package installed in the correct environment. 

In order to configure certain settings, you may need to comment/uncomment certain sections or lines of code under ```if __name__ == "__main__":```.
Additional comments are included within the python script for further guidance when running the script.

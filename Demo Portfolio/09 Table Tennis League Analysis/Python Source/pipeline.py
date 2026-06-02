from downloaders import download_all
from parsers import parse_all
from anonymizers import  anonymize_all

def run_all():
    """
    Executes a sequence of operations to download, parse, and anonymize data.

    This function is a high-level orchestrator that calls three other functions
    in sequence: ``download_all``, ``parse_all``, and ``anonymize_all``. Each step
    performs a specific operation required for data preprocessing.

    :return: None
    """
    # Download raw HTML pages
    download_all()
    # Parse downloaded HTML into CSV files
    parse_all()
    # Create anonymized versions of processed CSV files
    anonymize_all()
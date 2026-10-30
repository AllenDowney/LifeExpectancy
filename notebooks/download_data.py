"""Download data from Our World in Data for HALE gender gap analysis."""

import argparse
import os

import pandas as pd
import requests


def download_life_expectancy_gap(output_dir="data", filename=None, force=False):
    """Download life expectancy at birth by sex from OWID.
    
    This dataset contains life expectancy at birth for both females and males
    for various countries and years.
    
    Source: https://ourworldindata.org/grapher/life-expectation-at-birth-by-sex
    
    Parameters
    ----------
    output_dir : str, default "data"
        Directory to save the downloaded CSV file
    filename : str, optional
        Name of the output file. If None, uses default name.
    force : bool, default False
        If True, download the data even if the file already exists.
        If False, load from existing file if it exists.
        
    Returns
    -------
    pd.DataFrame
        The downloaded data as a pandas DataFrame
        
    Examples
    --------
    >>> df = download_life_expectancy_gap()
    >>> df.head()
    """
    # Dataset name from the OWID URL
    dataset_name = "life-expectation-at-birth-by-sex"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Set default filename if not provided
    if filename is None:
        filename = f"{dataset_name}.csv"
    
    # Construct the output file path
    output_path = os.path.join(output_dir, filename)
    
    # Check if file already exists
    if os.path.exists(output_path) and not force:
        print(f"File already exists: {output_path}")
        print("Loading from existing file. Use force=True to re-download.")
        df = pd.read_csv(output_path)
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        return df
    
    # Construct the CSV download URL with query parameters
    base_url = "https://ourworldindata.org/grapher"
    csv_url = f"{base_url}/{dataset_name}.csv?v=1&csvType=full&useColumnShortNames=true"
    
    print(f"Downloading data from: {csv_url}")
    
    # Download the data using pandas read_csv with User-Agent header
    storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'}
    df = pd.read_csv(csv_url, storage_options=storage_options)
    
    # Save to file
    df.to_csv(output_path, index=False)
    print(f"Data saved to: {output_path}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    return df


if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Download life expectancy gender gap data from Our World in Data"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if file already exists"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="Directory to save the downloaded CSV file (default: data)"
    )
    parser.add_argument(
        "--filename",
        type=str,
        default=None,
        help="Name of the output file (default: auto-generated)"
    )
    
    args = parser.parse_args()
    
    # Download the data when script is run directly
    df = download_life_expectancy_gap(
        output_dir=args.output_dir,
        filename=args.filename,
        force=args.force
    )
    print("\nFirst few rows:")
    print(df.head())


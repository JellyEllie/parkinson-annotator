#!/usr/bin/env python3

import pandas as pd
import os

# Script to load all patient CSVs and VCFs in ParkCSV/ as DataFrames named after the file
import os
import pandas as pd

dataframes = {}

def standardise_columns(df):
    # Remove spaces and lowercase all column names
    df.columns = df.columns.str.strip().str.lower()
    
    # Map known column names to standard names
    df = df.rename(columns={
        "#chrom": "chromosome",
        "chrom": "chromosome",
        "pos": "position",
        "id": "variant_id",
        "ref": "ref",
        "alt": "alt"
    })
    
    return df


def load_csvs(csv_dir="ParkCSV"):
    """Load all CSV files from the given directory into DataFrames."""
    for filename in os.listdir(csv_dir):
        if filename.endswith(".csv"):
            base = os.path.splitext(filename)[0]
            path = os.path.join(csv_dir, filename)
            df = pd.read_csv(path)
            df = standardise_columns(df)
            dataframes[base] = df
            print(f"Loaded CSV '{filename}' -> DataFrame '{base}' ({len(df)} rows)") #logs function on terminal
    return dataframes


def load_vcfs(vcf_dir="ParkVCF"):
    """Load all VCF files from the directory into DataFrames."""
    for filename in os.listdir(vcf_dir):
        if filename.endswith(".vcf"):
            path = os.path.join(vcf_dir, filename)
            # Define column names for VCF files
            column_names = ["chromosome", "position", "id", "ref", "alt"]
            # Use pandas to read VCF, automatically skipping comment lines
            df = pd.read_csv(path, sep="\t", comment="#", names=column_names, dtype=str)
            name = os.path.splitext(filename)[0] + "_vcf"
            dataframes[name] = df
            print(f"Loaded '{filename}' -> DataFrame '{name}' ({len(df)} rows)") #logs function on terminal
    return dataframes

#Test run both loaders
load_csvs()
load_vcfs()

#Optional: Test loading all files
if __name__ == "__main__":
    load_csvs()
    load_vcfs()
    print("\nAll DataFrames loaded. Columns standardized:")
    for name, df in dataframes.items():
        print(name, df.columns.tolist())


#hgvs nomenclature extractor to populate id column"
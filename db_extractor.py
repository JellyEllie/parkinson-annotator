#!/usr/bin/env python3
"""Script to load all patient CSVs and VCFs in ParkCSV/ and ParkVCF/ as DataFrames named after the file"""
import os
import pandas as pd

dataframes = {}

def standardise_columns(df):
    """Standardise column names for DataFrames.
    inputs:
        df (pd.DataFrame): DataFrame with original column names.
    returns:
        pd.DataFrame: DataFrame with standardised column names."
    """
    # Remove spaces and lowercase all column names
    df.columns = df.columns.str.strip().str.lower()
    # Map known column names to standard names
    df = df.rename(columns={
        "#chrom": "chromosome",
        "pos": "position",
        "id": "variant_id",
        "ref": "ref",
        "alt": "alt"
    })
    
    return df


def load_csvs(csv_dir="ParkCSV"):
    """Load all CSV files from the given directory into DataFrames.
    inputs: 
        csv_dir (str): Directory containing CSV files.
    returns:
        dict: Dictionary of DataFrames keyed by file base names."""
    for filename in os.listdir(csv_dir):
        if filename.endswith(".csv"):                                           #only process CSV files
            base = os.path.splitext(filename)[0]                                #get base name without ".csv" extension
            path = os.path.join(csv_dir, filename)                              #full path to file
            df = pd.read_csv(path)                                              #load CSV into DataFrame
            df = standardise_columns(df)                                        #standardise column names
            dataframes[base] = df                                               #store DataFrame in dictionary      
            print(f"Loaded CSV '{filename}' -> DataFrame '{base}' ({len(df)} rows)") #TEST: logs function on terminal
    return dataframes


def load_vcfs(vcf_dir="ParkVCF"):
    """Load all VCF files from the directory into DataFrames.
    inputs:
        vcf_dir (str): Directory containing VCF files.
    returns:
        dict: Dictionary of DataFrames keyed by file base names."""
    for filename in os.listdir(vcf_dir):                                        
        if filename.endswith(".vcf"):                                          #only process VCF files
            path = os.path.join(vcf_dir, filename)                             #full path to file
            column_names = ["chromosome", "position", "id", "ref", "alt"]       #standard VCF columns
            
            df = pd.read_csv(path, sep="\t", comment="#", names=column_names, dtype=str) #Use pandas to read VCF, automatically skipping comment lines
            name = os.path.splitext(filename)[0] + "_vcf"                               #DataFrame name with "_vcf" suffix
            dataframes[name] = df                                                       #store DataFrame in dictionary    
            print(f"Loaded '{filename}' -> DataFrame '{name}' ({len(df)} rows)")        #TEST:logs function on terminal
    return dataframes


#TEST: loading all files
if __name__ == "__main__":
    load_csvs()
    load_vcfs()
    print("\nAll DataFrames loaded. Columns standardized:")
    for name, df in dataframes.items():
        print(name, df.columns.tolist())
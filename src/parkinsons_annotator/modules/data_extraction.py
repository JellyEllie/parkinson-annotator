#!/usr/bin/env python3
"""
Loads all patient variant files (CSV and VCF) from ParkCSV/ and ParkVCF/,
parses them into DataFrames, and inserts the data into the parkinsons_data.db
SQLite database with proper patient–variant relationships.
"""

import os
import pandas as pd
from pathlib import Path
import sqlite3
from logger import logger

dataframes = {}
data_columns = ["chromosome", "position", "id", "ref", "alt", "hgvs"]
data_params = {
    ".csv": {"sep": ",", "names": data_columns, "dtype": str, "skiprows": 1},
    ".vcf": {"sep": "\t", "comment": "#", "names": data_columns, "dtype": str}
}

def load_raw_data(path="../data/"):
    """
    Load all CSV and VCF files in given path into DataFrames stored in 'dataframes' dict.

    Parameters:
    path (str): Path to directory containing data files.

    Returns:
    None: DataFrames are stored in global 'dataframes' dict.
    """
    for raw_file in Path(path).rglob("*"): # Recursively find all files in 'data' directory
        if raw_file.suffix in data_params: # Check if file extension exists in data_params
            df = pd.read_csv(raw_file, **data_params[raw_file.suffix]) # Load file into DataFrame with appropriate parameters
            dataframes[raw_file.stem] = df # Store DataFrame in dictionary with file base (stem) name as key
            logger.info(f"Loaded {raw_file.name}") # Log loading

def insert_dataframe_to_db(name, df, db_path="parkinsons_data.db"):
    """
    Insert patient and variant data from a DataFrame into SQLite,
    and link the patient to variants via the patient_variant junction table.
    
    Assumes variants table uses a composite primary key:
    (chromosome, position, ref, alt)

    Parameters:
    name (str): Patient name.
    df (pd.DataFrame): DataFrame containing variant data.
    db_path (str): Path to SQLite database.

    Returns:
    None

    Raises:
    sqlite3.DatabaseError: If there is an error inserting data into the database.
    """
    # Open DB connection
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # Expected columns for variants
    expected_cols = ["chromosome", "position", "ref", "alt", "hgvs",
                     "classification", "gene_symbol", "clinvar_id"]
    
    # Fill missing columns with None
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None
    
    # Insert patient if not exists
    cur.execute("INSERT OR IGNORE INTO patients (name) VALUES (?)", (name,))
    
    # Insert variants and link to patient
    for _, row in df.iterrows():
        values = tuple(row[col] for col in expected_cols)
        
        # Insert variant (replace if same composite key exists)
        cur.execute("""
            INSERT OR REPLACE INTO variants
            (chromosome, position, ref, alt, hgvs, classification, gene_symbol, clinvar_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, values)
        
        # Link patient to variant in junction table using foreign key entries
        cur.execute("""
            INSERT OR IGNORE INTO patient_variant
            (patient_name, chromosome, position, ref, alt)
            VALUES (?, ?, ?, ?, ?)
        """, (name, row["chromosome"], row["position"], row["ref"], row["alt"]))
    
    conn.commit()
    conn.close()
    logger.info(f"Inserted {len(df)} variants for patient '{name}' into the database.")

def load_and_insert_data():
    data_path = "../data/" # Path to data or upload directory
    load_raw_data(data_path)

    # Insert all loaded DataFrames into the database
    for name, df in dataframes.items():
        insert_dataframe_to_db(name, df)

if __name__ == "__main__":
    load_and_insert_data()
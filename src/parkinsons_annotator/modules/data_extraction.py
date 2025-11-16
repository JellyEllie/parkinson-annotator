#!/usr/bin/env python3
"""
Loads all patient variant files (CSV and VCF) from ParkCSV/ and ParkVCF/,
parses them into DataFrames, and inserts the data into the parkinsons_data.db
SQLite database with proper patient–variant relationships.
"""

import os
import pandas as pd
from pathlib import Path
import time
from dotenv import load_dotenv

from parkinsons_annotator.utils.variantvalidator_fetch import fetch_variant_validator
from parkinsons_annotator.utils.clinvar_fetch import fetch_clinvar_record
from parkinsons_annotator.logger import logger
from parkinsons_annotator.modules.db import get_db_session
from .models import Variant, Patient, Connector

load_dotenv()

dataframes = {}
data_columns = data_columns = [
    "chromosome", "position", "id", "ref", "alt", "hgvs",
    "gene_symbol", "cdna_change", "clinvar_id", "clinvar_accession",
    "classification", "num_submissions", "review_status", "condition", "clinvar_url"
]

data_params = {
    ".csv": {"sep": ",", "names": data_columns, "dtype": str, "skiprows": 1},
    ".vcf": {"sep": "\t", "comment": "#", "names": data_columns, "dtype": str}
}

# Mapping from ClinVar dict keys to your DataFrame columns
CLINVAR_FIELDS = {
    "Gene symbol": "gene_symbol",
    "cDNA change": "cdna_change",
    "ClinVar variant ID": "clinvar_id",
    "ClinVar accession": "clinvar_accession",
    "ClinVar consensus classification": "classification",
    "Number of submitted records": "num_submissions",
    "Review status": "review_status",
    "Associated condition": "condition",
    "ClinVar record URL": "clinvar_url"
}

def load_raw_data(path):
    """
    Load all CSV and VCF files in given path into DataFrames stored in 'dataframes' dict.

    Parameters:
    path (str): Path to directory containing data files.

    Returns:
    None: DataFrames are stored in global 'dataframes' dict.
    """
    for raw_file in Path(path).glob("*"): # Recursively find all files in 'data' directory
        if raw_file.suffix in data_params: # Check if file extension exists in data_params
            df = pd.read_csv(raw_file, **data_params[raw_file.suffix]) # Load file into DataFrame with appropriate parameters
            dataframes[raw_file.stem] = df # Store DataFrame in dictionary with file base (stem) name as key
            logger.info(f"Loaded {raw_file.name}") # Log loading


def fill_variant_id(df: pd.DataFrame) -> pd.DataFrame:
    """Fill the 'id' column using chromosome:position:ref:alt."""
    df['id'] = df.apply(lambda r: f"{r.chromosome}:{r.position}:{r.ref}:{r.alt}", axis=1)
    return df


def enrich_hgvs(df):
    """
    Enrich the 'hgvs' column for all variants in the loaded DataFrames
    using the VariantValidator API.
    """
    missing_hgvs = df['hgvs'].isna() | (df['hgvs'] == '')
    for idx in df[missing_hgvs].index:
        try:
            hgvs_data = fetch_variant_validator(df.at[idx, 'id'])
            df.at[idx, 'hgvs'] = hgvs_data.get('HGVS nomenclature', None)
        except Exception as e:
            logger.error(f"Error retrieving HGVS for variant {df.at[idx, 'id']}: {e}")
            df.at[idx, 'hgvs'] = None
    return df

def enrich_clinvar(df):
    # Only rows where clinvar_id is missing
    missing = df['clinvar_id'].isna() | (df['clinvar_id'] == '')
    for idx in df[missing].index:
        hgvs = df.at[idx, 'hgvs']
        if not hgvs:
            continue  # skip if HGVS missing

        try:
            clinvar_data = fetch_clinvar_record(hgvs)
            #time.sleep(0.3)  # optional throttle to avoid rate limits
        except Exception as e:
            logger.error("Error fetching ClinVar for %s: %s", hgvs, e)
            clinvar_data = {k: None for k in CLINVAR_FIELDS.keys()}

        # Fill the DataFrame columns
        for field, col in CLINVAR_FIELDS.items():
            df.at[idx, col] = clinvar_data.get(field)

    return df

def insert_dataframe_to_db(name, df):
    """
    Insert patient and variant data from a DataFrame into SQLite,
    and link the patient to variants via the patient_variant junction table.
    
    Assumes variants table uses a composite primary key:
    (chromosome, position, ref, alt)

    Parameters:
    name (str): Patient name.
    df (pd.DataFrame): DataFrame containing variant data.

    Returns:
    None
    """
    # Get DB session
    db_session = get_db_session()

    # Expected columns for variants
    # expected_cols = ["chromosome", "position", "ref", "alt", "hgvs",
    #                  "classification", "gene_symbol", "clinvar_id"]
    expected_cols = [
        "id", "chromosome", "position", "ref", "alt", "hgvs",
        "classification", "gene_symbol", "clinvar_id", "clinvar_accession",
        "num_submissions", "review_status", "associated_condition", "clinvar_url"
    ]
    # Fill missing columns with None
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None
    
    # Insert patient if not exists
    # cur.execute("INSERT OR IGNORE INTO patients (name) VALUES (?)", (name,))
    
    # Ensure patient exists
    patient = db_session.get(Patient, name)
    if not patient:
        patient = Patient(name=name)
        db_session.add(patient)
        db_session.commit()
    
    # Iterate variants
    for _, row in df.iterrows():
        variant = db_session.get(Variant, row["id"])
        if not variant:
            variant = Variant(
                id=row["id"],
                chromosome=int(row["chromosome"]),
                position=int(row["position"]),
                ref=row["ref"],
                alt=row["alt"],
                hgvs=row.get("hgvs"),
                classification=row.get("classification"),
                gene_symbol=row.get("gene_symbol"),
                clinvar_id=row.get("clinvar_id"),
                cdna_change=row.get("cdna_change"),
                clinvar_accession=row.get("clinvar_accession"),
                num_submissions=row.get("num_submissions"),
                review_status=row.get("review_status"),
                associated_condition=row.get("condition"),
                clinvar_url=row.get("clinvar_url")
            )
            db_session.add(variant)
        
        # Link patient to variant
        link = db_session.get(Connector, (name, row["id"]))
        if not link:
            link = Connector(patient_name=name, variant_id=row["id"])
            db_session.add(link)

    # # Insert variants and link to patient
    # for _, row in df.iterrows():
    #     values = tuple(row[col] for col in expected_cols)
        
    #     # Insert variant (replace if same composite key exists)
    #     cur.execute(f"""
    #             INSERT OR REPLACE INTO variants
    #             ({', '.join(expected_cols)})
    #             VALUES ({', '.join(['?'] * len(expected_cols))})
    #         """, values)
        
    #     # Link patient to variant in junction table using foreign key entries
    #     cur.execute("""
    #         INSERT OR IGNORE INTO patient_variant
    #         (patient_name, variant_id)
    #         VALUES (?, ?)
    #     """, (name, row["id"]))

    # conn.commit()
    # conn.close()
    logger.info(f"Inserted {len(df)} variants for patient '{name}' into the database.")


def load_and_insert_data():
    # data_path = "../uploads/" # Path to data or upload directory
    data_path = os.getenv("UPLOAD_FOLDER")
    logger.info(f"Loading data from: {data_path}")
    logger.info(f"Database path: {Path(data_path)}")
    
    load_raw_data(data_path)

    for patient_name, df in dataframes.items():
        df = (df
            .pipe(fill_variant_id)
            .pipe(enrich_hgvs)
            .pipe(enrich_clinvar)
            )
        insert_dataframe_to_db(patient_name, df)

    print(dataframes.keys())
    print(dataframes['Patient1'].head())
    # Insert all loaded DataFrames into the database

if __name__ == "__main__":
    load_and_insert_data()
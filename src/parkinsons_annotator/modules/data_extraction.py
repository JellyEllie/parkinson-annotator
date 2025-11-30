#!/usr/bin/env python3
"""
data_extraction.py

Loads all patient variant files (CSV and VCF) from ParkCSV/ and ParkVCF/,
parses them into DataFrames, and inserts the data into the parkinsons_data.db
SQLite database with proper patient–variant relationships.

"""

import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import time

from flask import current_app
from parkinsons_annotator.logger import logger
from parkinsons_annotator.modules.db import get_db_session
from .models import Genes, Variant, Patient, Connector
from parkinsons_annotator.utils.variantvalidator_fetch import fetch_variant_validator
from parkinsons_annotator.utils.clinvar_fetch import fetch_clinvar_record
from parkinsons_annotator.utils.clinvar_fetch import ClinVarIDNotFoundError, ClinVarConnectionError, HGVSFormatError

load_dotenv()

dataframes = {}

# Full list of columns; CSV can have fewer, missing columns will be added as None and later overwritten
data_columns = [
    "chromosome", "position", "id", "ref", "alt", "vcf_form", "hgvs",
    "gene_symbol", "cdna_change", "clinvar_id", "clinvar_accession",
    "classification", "num_records", "review_status", "associated_condition", "clinvar_url"
]

# Read parameters for CSV/VCF files:
# 'names' forces column names to match data_columns, 'skiprows' skips header row of CSV
data_params = {
    ".csv": {"sep": ",", "names": data_columns, "dtype": str, "skiprows": 1},
    ".vcf": {"sep": "\t", "comment": "#", "names": data_columns, "dtype": str}
}

# Mapping from ClinVar keys to DataFrame columns
CLINVAR_FIELDS = {
    "Gene symbol": "gene_symbol",
    "cDNA change": "cdna_change",
    "ClinVar variant ID": "clinvar_id",
    "ClinVar accession": "clinvar_accession",
    "ClinVar consensus classification": "classification",
    "Number of submitted records": "num_records",
    "Review status": "review_status",
    "Associated condition": "associated_condition",
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
            df = pd.read_csv(raw_file, **data_params[raw_file.suffix]) # Load file into df with appropriate parameters
            # Ensure all columns exist
            for col in data_columns:
                if col not in df.columns:
                    df[col] = None # Add missing columns as None if not contained in file
            dataframes[raw_file.stem] = df # Store DataFrame in dictionary with file base (stem) name as key
            logger.info(f"Loaded {raw_file.name}") # Log loading

def load_single_file(file_path):
    """
        Load one CSV or VCF file into the global dataframes dict.
        Used in upload route to avoid reloading all existing files in upload directory when uploading a new file.

        Parameters:
        file_path (str): Path to file to load. Must be a CSV or VCF file.

        Returns:
        None: DataFrames are stored in global 'dataframes' dict.
    """

    raw_file = Path(file_path)

    if raw_file.suffix not in data_params:
        raise ValueError(f"Unsupported file type: {raw_file.suffix}")

    # Load file
    df = pd.read_csv(raw_file, **data_params[raw_file.suffix])

    # Ensure all required columns exist
    for col in data_columns:
        if col not in df.columns:
            df[col] = None

    # Store under patient name (filename without extension)
    dataframes[raw_file.stem] = df

    logger.info(f"Loaded single file: {raw_file.name}")

def fill_variant_notation(df: pd.DataFrame) -> pd.DataFrame:
    """Fill the 'vcf_form' column using chromosome:position:ref:alt."""
    df['vcf_form'] = df.apply(lambda r: f"{r.chromosome}:{r.position}:{r.ref}:{r.alt}", axis=1)
    return df

def enrich_hgvs(df, throttle: float = 0.3):
    """
    Enrich the 'hgvs' column for all variants in the loaded DataFrames
    using the VariantValidator API, with optional throttling.

    Parameters:
    df (pd.DataFrame): DataFrame with variant data.
    throttle (float): Seconds to wait between API calls.
    """
    missing_hgvs = df['hgvs'].isna() | (df['hgvs'] == '') # Collate rows where hgvs is missing (NA) or empty string

    for idx in df[missing_hgvs].index:
        try:
            # fetch HGVS from VV API using genomic notation and add to DataFrame
            hgvs_data = fetch_variant_validator(df.at[idx, 'vcf_form'])
            df.at[idx, 'hgvs'] = hgvs_data.get('HGVS nomenclature', None)
        except Exception as e:
            logger.error(f"Error retrieving HGVS for variant {df.at[idx, 'vcf_form']}: {e}")
            df.at[idx, 'hgvs'] = None
        # Throttle API calls
        if throttle > 0:
            time.sleep(throttle)
    return df

def enrich_clinvar(df, throttle: float = 0.3):
    """
    Enrich the 'clinvar' columns for all variants in the DataFrame
    using the ClinVar API, with optional throttling.

    Parameters:
    df (pd.DataFrame): DataFrame with variant data.
    throttle (float): Seconds to wait between API calls.

    Returns:
    pd.DataFrame: enriched DataFrame with ClinVar data.
    """
    # Only rows where clinvar_id is missing/empty string
    missing = df['clinvar_id'].isna() | (df['clinvar_id'] == '')

    for idx in df[missing].index:
        hgvs = df.at[idx, 'hgvs']
        if not hgvs:
            continue  # Skip if HGVS missing as ClinVar cannot be queried without it

        try:
            # Call ClinVar API - this may raise ClinVarIDNotFoundError
            clinvar_data = fetch_clinvar_record(hgvs)

            # Map ClinVar fields to DataFrame columns
            for field, col in CLINVAR_FIELDS.items():
                value = clinvar_data.get(field)
                df.at[idx, col] = value

        except (ClinVarIDNotFoundError, ClinVarConnectionError, HGVSFormatError) as e:
            # Variant not found in ClinVar or other ClinVar-specific error
            logger.warning(f"ClinVar lookup failed for {hgvs}: {e}")
            # Set all ClinVar fields to None for this variant
            for col in CLINVAR_FIELDS.values():
                df.at[idx, col] = None

        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error fetching ClinVar for {hgvs}: {e}")
            # Set all ClinVar fields to None for this variant
            for col in CLINVAR_FIELDS.values():
                df.at[idx, col] = None

        # Throttle API calls
        if throttle > 0:
            time.sleep(throttle)

    # Return enriched DataFrame
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
    # Get SQLAlchemy database session (to connect to DB)
    db_session = get_db_session()

    # Convert all NaN values to None to avoid SQL errors
    df = df.where(pd.notnull(df), "None")

    # Ensure patient exists
    patient = db_session.get(Patient, name)
    if not patient:
        patient = Patient(name=name)
        db_session.add(patient)
        db_session.commit()

    # Assign genomic notation as primary key
    for _, row in df.iterrows():
        # Skip rows with missing vcf_form and warn if so
        vcf_form = row["vcf_form"]
        if not vcf_form:
            logger.warning(f"Skipping variant with missing vcf_form for patient {name}")
            continue

        # Add gene to Genes table if missing
        gene_symbol = row.get("gene_symbol") or "UNKNOWN"
        if not db_session.get(Genes, gene_symbol):
            db_session.add(Genes(gene_symbol=gene_symbol, gene_url=""))
            db_session.flush()  # Flush communicates changes to DB to ensure data is visible so queries work

        # Insert variant
        variant = db_session.get(Variant, row["vcf_form"])
        if not variant:
            variant = Variant(
                hgvs=row.get("hgvs"),
                vcf_form=row.get("vcf_form"),
                clinvar_id=row.get("clinvar_id"),
                gene_symbol=gene_symbol,
                classification=row.get("classification"),
                cdna_change=row.get("cdna_change"),
                clinvar_accession=row.get("clinvar_accession"),
                num_records=row.get("num_records"),
                review_status=row.get("review_status"),
                associated_condition=row.get("associated_condition"),
                clinvar_url=row.get("clinvar_url")
            )
            db_session.add(variant)
            db_session.flush()

        # Link patient to variant via Connector table
        try:
            link_exists = db_session.query(Connector).filter_by(
                patient_name=name,
                variant_vcf_form=vcf_form
            ).first()
        except Exception as e:
            logger.error(f"Error querying Connector for patient {name}, variant {vcf_form}: {e}")
            link_exists = True  # Skip insert to avoid NoneType issues

        # Create link only if link is missing
        if not link_exists:
            db_session.add(Connector(patient_name=name, variant_vcf_form=row['vcf_form']))

    db_session.commit() # Commit all changes to DB permanently (finalises flushed changes)
    logger.info(f"Inserted {len(df)} variants for patient '{name}'.")

def load_and_insert_data():
    """Top-level function to load, enrich, and insert all patient data."""

    # Clear old data so it doesn't get reprocessed
    dataframes.clear()
    # Read upload folder from Flask app config
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    logger.info(f"Loading data from: {upload_folder}")
    #Load CSV and VCF files
    load_raw_data(upload_folder)

    # Enrich variant df with variant genomic notation, HGVS notation, and ClinVar data and insert into DB
    for patient_name, df in dataframes.items():
        df = (df.
              pipe(fill_variant_notation)
              .pipe(enrich_hgvs)
              .pipe(enrich_clinvar)
              )
        insert_dataframe_to_db(patient_name, df)

    logger.info(f"Finished processing {len(dataframes)} patient files.")
#!/usr/bin/env python3
"""
data_extraction.py

Loads all patient variant files (CSV and VCF) from ParkCSV/ and ParkVCF/,
parses them into DataFrames, and inserts the data into the parkinsons_data.db
SQLite database with proper patient–variant relationships.

"""
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


from flask import current_app
from parkinsons_annotator.logger import logger
from parkinsons_annotator.modules.db import get_db_session
from .models import Genes, Variant, Patient, Connector
from parkinsons_annotator.utils.variantvalidator_fetch import fetch_variant_validator
from parkinsons_annotator.utils.clinvar_fetch import extract_clinvar_annotation
from parkinsons_annotator.utils.clinvar_fetch import ClinVarIDNotFoundError, ClinVarConnectionError, HGVSFormatError
from parkinsons_annotator.utils.data_checks import existing_variant_check, compare_uploaded_vs_existing

load_dotenv()

# Dictionary to store loaded DataFrames by patient name
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
    for raw_file in Path(path).glob("*"):  # Recursively find all files in 'data' directory
        if raw_file.suffix in data_params:  # Check if file extension exists in data_params
            df = pd.read_csv(raw_file, **data_params[raw_file.suffix])  # Load file into df with appropriate parameters
            # Ensure all columns exist
            for col in data_columns:
                if col not in df.columns:
                    df[col] = None  # Add missing columns as None if not contained in file
            dataframes[raw_file.stem] = df  # Store DataFrame in dictionary with file base (stem) name as key
            logger.info(f"Loaded {raw_file.name}")  # Log loading


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


def enrich_hgvs(df, session, throttle: float = 0.3):
    """
    Enrich the 'hgvs' column for all variants in the loaded DataFrames
    using the VariantValidator API, with optional throttling. API calls are performed only
    if the variant is not already present in the database.

    Parameters:
    df (pd.DataFrame): DataFrame with variant data.
    throttle (float): Seconds to wait between API calls.
    """
    # Collate rows in patient's variant DataFrame where hgvs is missing or empty string
    missing_hgvs = df['hgvs'].isna() | (df['hgvs'] == '')
    for idx in df[missing_hgvs].index:
        # Get variant genomic notation from DataFrame
        vcf_form = df.at[idx, 'vcf_form']
        # Check if variant already exists in database
        existing_variant = existing_variant_check(vcf_form, session)
        if existing_variant:
            # Fill in HGVS from database
            logger.info("Skipping VV API call.")
            df.at[idx, 'hgvs'] = existing_variant['hgvs']
            continue  # Skip API call
        # Otherwise, fetch HGVS from VariantValidator API
        logger.info("Proceeding with VariantValidator API call")
        try:
            # fetch HGVS from VV API using genomic notation and add to DataFrame
            hgvs_data = fetch_variant_validator(vcf_form)
            df.at[idx, 'hgvs'] = hgvs_data.get('HGVS nomenclature', None)
        except Exception as e:
            logger.error(f"Error retrieving HGVS for variant {df.at[idx, 'vcf_form']}: {e}")
            df.at[idx, 'hgvs'] = None
        # Throttle API calls
        if throttle > 0:
            time.sleep(throttle)
    return df


def enrich_clinvar(df, session, throttle: float = 0.3):
    """
    Enrich the 'clinvar' columns for all variants in the DataFrame
    using the ClinVar API, with optional throttling. Skips API call if variant ClinVar data is already in database.

    Parameters:
    df (pd.DataFrame): DataFrame with variant data.
    throttle (float): Seconds to wait between API calls.

    Returns:
    pd.DataFrame: enriched DataFrame with ClinVar data.
    """
    # Only rows where clinvar_id is missing/empty string
    missing = df['clinvar_id'].isna() | (df['clinvar_id'] == '')

    for idx in df[missing].index:
        vcf_form = df.at[idx, 'vcf_form']
        hgvs = df.at[idx, 'hgvs']

        # Check whether variant already exists in database
        existing_variant = existing_variant_check(vcf_form, session)

        if existing_variant and existing_variant.get("clinvar_id"):
            # Fill DataFrame from database
            for col in CLINVAR_FIELDS.values():
                df.at[idx, col] = existing_variant.get(col)
            logger.info(f"ClinVar data loaded from DB for {vcf_form}")
            continue  # Skip API call

        if not hgvs:
            logger.warning(f"Skipping ClinVar API: Missing HGVS for {vcf_form}")
            continue  # Skip if HGVS missing as ClinVar cannot be queried without it

        # Otherwise, fetch ClinVar data from API
        try:
            # Call ClinVar API - this may raise ClinVarIDNotFoundError
            clinvar_data = extract_clinvar_annotation(hgvs)

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

    # Fill missing ClinVar fields with a default string
    for col in CLINVAR_FIELDS.values():
        df[col] = df[col].fillna("Not found in ClinVar")

    # Return enriched DataFrame
    return df


def insert_dataframe_to_db(name, df, session):
    """
    Insert patient and variant data from a DataFrame into SQLite,
    and link the patient to variants via the patient_variant junction table.

    Parameters:
    name (str): Patient name.
    df (pd.DataFrame): DataFrame containing variant data.

    Returns:
    None
    """
    # Convert all NaN values to None to avoid SQL errors
    df = df.where(pd.notnull(df), None)

    # Ensure patient exists
    patient = session.get(Patient, name)
    if not patient:
        patient = Patient(name=name)
        session.add(patient)

    # Assign genomic notation as primary key
    for _, row in df.iterrows():
        # Skip rows with missing vcf_form and warn if so
        vcf_form = row["vcf_form"]
        if not vcf_form:
            logger.warning(f"Skipping variant with missing vcf_form for patient {name}")
            continue

        # Add gene to Genes table if missing
        gene_symbol = row.get("gene_symbol") or "UNKNOWN"
        if not session.get(Genes, gene_symbol):
            session.add(Genes(gene_symbol=gene_symbol, gene_url=""))
            session.flush()  # Flush communicates changes to DB to ensure data is visible so queries work

        # Insert variant
        variant = session.get(Variant, row["vcf_form"])
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
            session.add(variant)
            session.flush()

        # Link patient to variant via Connector table
        try:
            link_exists = session.query(Connector).filter_by(
                patient_name=name,
                variant_vcf_form=vcf_form
            ).first()
        except Exception as e:
            logger.error(f"Error querying Connector for patient {name}, variant {vcf_form}: {e}")
            link_exists = True  # Skip insert to avoid NoneType issues

        # Create link only if link is missing
        if not link_exists:
            session.add(Connector(patient_name=name, variant_vcf_form=row['vcf_form']))

    logger.info(f"Prepared {len(df)} variants for patient '{name}' to be committed.")


def load_and_insert_data():
    """
    Top-level function to load, enrich, and insert all patient data.

    Manages (commits and closes) its own database session.
    """

    # Clear old data so it doesn't get reprocessed
    dataframes.clear()
    # Read upload folder from Flask app config
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    logger.info(f"Loading data from: {upload_folder}")
    #Load CSV and VCF files
    load_raw_data(upload_folder)

    session = get_db_session()

    # Insert data into DB once patient variants have been checked to ensure the same patient variants are not uploaded
    try:
        for patient_name, df in dataframes.items():
            # Check whether variants for a patient have been uploaded before
            result = compare_uploaded_vs_existing(patient_name, df, session)
            # If patient exists and variants are unchanged, skip processing
            if result["exists"] and result["identical"]:
                logger.info(f"Patient '{patient_name}'already uploaded with identical variants. Skipping upload.")
                continue
            # Enrich variant df with variant genomic notation, HGVS notation, and ClinVar data and insert into DB
            df = (df.
                  pipe(fill_variant_notation)
                  .pipe(enrich_hgvs, session)
                  .pipe(enrich_clinvar, session)
                  )
            insert_dataframe_to_db(patient_name, df, session)
        # Commit all changes to DB permanently (finalises flushed changes from insert_dataframe_to_db)
        session.commit()
        logger.info(f"Finished processing {len(dataframes)} patient files.")
    except Exception as e:
        logger.error(f"Error during load_and_insert_data: {e}")
        session.rollback()
        raise
    finally:
        # Close session
        session.close()
    logger.info(f"Finished processing {len(dataframes)} patient files.")
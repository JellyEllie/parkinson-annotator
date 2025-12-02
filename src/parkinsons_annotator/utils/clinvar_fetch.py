"""
This script uses the Biopython Entrez module to query the ClinVar NCBI database. 
For a given variant in HGVS notation (e.g. "NM_001377265.1:c.841G>T"), the script
retrieves annotation information such as consensus classification, number of submissions,
review status and associated condition. 

References:
Biopython Tutorial and Cookbook, "Accessing NCBI’s Entrez databases"
(https://biopython.org/docs/dev/Tutorial/chapter_entrez.html)
"""

import json
import os
from Bio import Entrez  # Import Entrez module from Biopython for NCBI queries
from dotenv import load_dotenv
from src.parkinsons_annotator.logger import logger


load_dotenv()  # Load environment variables from .env file

# NCBI Entrez requires a valid email to identify the user
Entrez.email = os.getenv("ENTREZ_EMAIL")  # Set email (required by NCBI Entrez API)


class HGVSFormatError(Exception):
    """Custom exception raised when the HGVS string is not in the appropriate format."""
    pass


class ClinVarIDFormatError(Exception):
    """Custom exception raised when the ClinVar ID string is not in the appropriate format."""
    pass


class ClinVarConnectionError(Exception):
    """Custom exception raised when unable to connect to the NCBI ClinVar API"""
    pass


class ClinVarIDNotFoundError(Exception):
    """Custom exception raised when there is no ClinVar ID for the given variant."""
    pass


class ClinVarESummaryError(Exception):
    """Custom exception raised when the ClinVar ESummary response does not contain the expected format, to extract ClinVar annotation fields."""
    pass


def fetch_clinvar_id(hgvs_variant):
    """
    This function queries the NCBI ClinVar database using the Entrez API, to obtain the ClinVar ID
    for a variant in HGVS notation.
    
    Parameters:
    hgvs_variant (str): A variant in HGVS notation (e.g. "NM_001377265.1:c.841G>T").

    Returns:
    str: ClinVar variant ID.
    
    Raises:
    HGVSFormatError: If the HGVS variant does not have the expected format (e.g. "NM_001377265.1:c.841G>T").
    ClinVarConnectionError: If there is an NCBI ClinVar API error.
    ClinVarIDNotFoundError: If there is no ClinVar ID for the variant.
    """

    logger.info(f"Fetching ClinVar ID for the variant: {hgvs_variant}.")

    # Ensure input variant is a string
    if not isinstance(hgvs_variant, str):
        logger.error("Variant description is not a string.")
        raise HGVSFormatError("Variant description must be a string.")


    # Validate HGVS format of variant
    # Expected format must include transcript accession 'NM_', a colon and a cDNA notation 'c.'
    if not (hgvs_variant.startswith("NM_") and ":" in hgvs_variant and "c." in hgvs_variant):
        logger.error("Variant format is not the HGVS transcript format.")
        raise HGVSFormatError(
            f"Invalid HGVS format: {hgvs_variant}. "
            "Expected transcript HGVS e.g. 'NM_001377265.1:c.841G>T'. "
        )


    # Search ClinVar for variant ClinVar ID
    try:
        handle = Entrez.esearch(db="clinvar", term=hgvs_variant)  # Open connection to ClinVar and query database via Entrez ESearch using the HGVS-formatted variant
        record = Entrez.read(handle)  # Parse XML response from ESearch into a Python dictionary
        handle.close()  # Close connection
        logger.info("NCBI Entrez API request is successful.")
    except Exception as e:
        logger.error("Connection to the NCBI Entrez API was unsuccessful during ClinVar ESearch.")
        logger.exception("Unable to connect to NCBI Entrez API during ClinVar ESearch.")
        raise ClinVarConnectionError(f"Unable to connect to NCBI Entrez API during ClinVar ESearch: {e}") from e

    if not record.get("IdList"):
        logger.warning(f"No ClinVar ID found for variant '{hgvs_variant}'.")
        raise ClinVarIDNotFoundError(f"Variant '{hgvs_variant}' not found in ClinVar.")


    clinvar_id = record["IdList"][0]

    return clinvar_id


def fetch_clinvar_esummary(clinvar_id):
    """
    This function queries the NCBI ClinVar ESummary for a given ClinVar ID, and obtains the variant summary.

    Parameters:
    clinvar_id (str): A ClinVar variant ID.

    Returns:
    dict: ClinVar ESummary.

    Raises:
    ClinVarIDFormatError: If the ClinVar ID does not have the expected format.
    ClinVarConnectionError: If ESummary fails due to an NCBI ClinVar API error.
    ClinVarESummaryError: If the ClinVar ESummary response does not contain the expected format to extract ClinVar annotation fields.
    """

    logger.info(f"Fetching ClinVar ESummary for the ClinVar ID: {clinvar_id}.")

    # Ensure input ClinVar ID is a string
    if not isinstance(clinvar_id, str):
        logger.error("ClinVar ID is not a string.")
        raise ClinVarIDFormatError("ClinVarID must be a string.")


    # Fetch ClinVar ESummary using ClinVar ID
    try:
        handle = Entrez.esummary(db="clinvar", id=clinvar_id)  # Open connection to ClinVar and query database via Entrez ESummary using the ClinVar ID
        summary = Entrez.read(handle, validate=False)  # Parse XML response from ESummary into a Python dictionary
        handle.close()  # Close connection
        logger.info("ClinVar ESummary request is successful.")
    except Exception as e:
        logger.error("Connection to the NCBI Entrez API was unsuccessful during ClinVar ESummary.")
        logger.exception("Unable to connect to ClinVar during ESummary:")
        raise ClinVarConnectionError(f"Unable to connect to ClinVar during ESummary: {e}") from e
    
    try:
        summary["DocumentSummarySet"]["DocumentSummary"][0]
    except Exception as e:
        logger.error("Unable to extract the main ClinVar DocumentSummary entry from the ESummary response.")
        logger.exception("ClinVar ESummary response missing expected 'DocumentSummary' entry.")
        raise ClinVarESummaryError(f"ClinVar ESummary response did not contain the expected 'DocumentSummary' entry: {e}") from e
    
    clinvar_doc = summary["DocumentSummarySet"]["DocumentSummary"][0]

    return clinvar_doc


def extract_clinvar_annotation(hgvs_variant):
    """
    This function fetches the ClinVar ID and ClinVar annotation summary from the NCBI ClinVar database using the
    Entrez API for a given HGVS variant. It extracts key annotation fields (e.g. gene symbol, cDNA change, classification,
    review status, number of submissions, associated condition, and ClinVar URL).
    
    Parameters:
    hgvs_variant (str): A variant in HGVS transcript notation (e.g. "NM_001377265.1:c.841G>T").

    Returns:
    dict: Dictionary containing extracted ClinVar annotation fields.
    
    Raises:
    HGVSFormatError: If the HGVS variant does not have the expected format (e.g. "NM_001377265.1:c.841G>T").
    ClinVarIDFormatError: If the ClinVar ID does not have the expected format.
    ClinVarConnectionError: If there is an NCBI ClinVar API error.
    ClinVarIDNotFoundError: If there is no ClinVar ID for the variant.
    ClinVarESummaryError: If the ClinVar ESummary response does not contain the expected format, to extract ClinVar annotation fields.
    """

    logger.info(f"Fetching ClinVar annotation for the variant: {hgvs_variant}.")

    # Ensure input variant is a string
    if not isinstance(hgvs_variant, str):
        logger.error("Variant description is not a string.")
        raise HGVSFormatError("Variant description must be a string.")


    # Validate HGVS format of variant
    # Expected format must include transcript accession 'NM_', a colon and a cDNA notation 'c.'
    if not (hgvs_variant.startswith("NM_") and ":" in hgvs_variant and "c." in hgvs_variant):
        logger.error("Variant format is not the HGVS transcript format.")
        raise HGVSFormatError(
            f"Invalid HGVS format: {hgvs_variant}. "
            "Expected transcript HGVS e.g. 'NM_001377265.1:c.841G>T'. "
        )
    
    # Fetch the ClinVar ID for the given HGVS variant
    clinvar_id = fetch_clinvar_id(hgvs_variant)

    # Fetch the ClinVar ESummary record for the ClinVar ID
    clinvar_doc = fetch_clinvar_esummary(clinvar_id)


    # Extract key fields from ClinVar ESummary
    try:
        gene_symbol = clinvar_doc["genes"][0]["symbol"]
        logger.debug(f"Extracted gene symbol: {gene_symbol}")
    except (KeyError, IndexError, TypeError):
        logger.warning("Gene symbol not found in ClinVar ESummary.")
        gene_symbol = "N/A"
    
    try:
        cdna_change = clinvar_doc["variation_set"][0]["cdna_change"]
        logger.debug(f"Extracted cDNA change: {cdna_change}.")
    except (KeyError, IndexError, TypeError):
        logger.warning("cDNA change not found in ClinVar ESummary.")
        cdna_change = "N/A"

    try:
        accession = clinvar_doc["accession"]
        logger.debug(f"Extracted ClinVar accession: {accession}.")
    except (KeyError, IndexError, TypeError):
        logger.warning("ClinVar accession not found in ClinVar ESummary.")
        accession = "N/A"

    try:
        classification = clinvar_doc["germline_classification"]["description"]
        logger.debug(f"Extracted ClinVar consensus classification: {classification}.")
    except (KeyError, IndexError, TypeError):
        logger.warning("ClinVar consensus classification not found in ClinVar ESummary.")
        classification = "N/A"
    
    try:
        scv_list = clinvar_doc["supporting_submissions"]["scv"]
        num_submissions = len(scv_list)
        logger.debug(f"Extracted number of submitted records: {num_submissions}.")
    except (KeyError, IndexError, TypeError):
        logger.warning("Number of submitted records not found in ClinVar ESummary.")
        num_submissions = "N/A"

    try:
        review_status = clinvar_doc["germline_classification"]["review_status"]
        logger.debug(f"Extracted review status: {review_status}.")
    except (KeyError, IndexError, TypeError):
        logger.warning("Review status not found in ClinVar ESummary.")
        review_status = "N/A"

    try:
        condition_name = clinvar_doc["germline_classification"]["trait_set"][0]["trait_name"]
        logger.debug(f"Extracted associated condition: {condition_name}.")
    except (KeyError, IndexError, TypeError):
       logger.warning("Associated conditions not found in ClinVar ESummary.")
       condition_name = "N/A"
    

    # Fetch ClinVar URL
    clinvar_url = f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{clinvar_id}"


    return {
        "Gene symbol": gene_symbol,  
        "cDNA change": cdna_change,
        "ClinVar variant ID": clinvar_id,
        "ClinVar accession": accession,
        "ClinVar consensus classification": classification,
        "Number of submitted records": num_submissions,
        "Review status": review_status,
        "Associated condition": condition_name,
        "ClinVar record URL": clinvar_url,
    }

if __name__ == "__main__":  # pragma: no cover

    hgvs_variant = "NM_001377265.1:c.841G>T"
    clinvar_output= extract_clinvar_annotation(hgvs_variant)
    print(json.dumps(clinvar_output, indent=4))
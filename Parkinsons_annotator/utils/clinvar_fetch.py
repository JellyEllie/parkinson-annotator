"""
This script uses the Biopython Entrez module to query the ClinVar NCBI database. 
For a given a variant in HGVS notation, it retrieves annotation information such as:
consensus classification, number of submissions, review status, associated condition. 
The script outputs this information and the ClinVar record URL.

Custom exceptions are raised for HGVS format errors, connection errors, missing ClinVar
IDs, and unexpected response formats.

References:
Biopython Tutorial and Cookbook, "Accessing NCBI’s Entrez databases"
(https://biopython.org/docs/dev/Tutorial/chapter_entrez.html)
"""

import json
from Bio import Entrez  # Import Entrez module from Biopython for NCBI queries

# NCBI Entrez requires a valid email to identify the user
Entrez.email = "naima.abdi@postgrad.manchester.ac.uk"  # Set email (required by NCBI Entrez API)


class HGVSFormatError(Exception):
    """Custom exception raised when the HGVS string is not in the appropriate format."""
    pass


class ClinVarConnectionError(Exception):
    """Custom exception raised when unable to connect to the NCBI ClinVar API e.g. during ESearch or ESummary."""
    pass


class ClinVarIDNotFoundError(Exception):
    """Custom exception raised when there is no ClinVar ID for the given variant."""
    pass


class ClinVarESummaryError(Exception):
    """Custom exception raised when the ClinVar ESummary response is missing expected fields."""
    pass


class ClinVarFieldMissingError(Exception):
    """Custom exception raised when an expected field is missing or malformed in the ClinVar ESummary response."""
    pass


def fetch_clinvar_record(hgvs_variant):
    """
    This function fetches a ClinVar record from the NCBI ClinVar database using the
    Entrez API. For a variant in HGVS notation, the ClinVar record and its ESummary are
    both returned as Python dictionaries.

    Parameters:
    hgvs_variant (str): A variant in HGVS notation. Must contain ":" and "c."
    (e.g. "NM_001377265.1:c.841G>T")

    Returns:
    dict: A Python dictionary representation of the ClinVar record and ESummary.

    Raises:
    HGVSFormatError: If the HGVS variant does not have the expected ":" and "c." format.
    ClinVarConnectionError: If there is a NCBI ClinVar API error
    ClinVarIDNotFoundError: If there is no ClinVar ID for the variant
    ClinVarESummaryError: If the ClinVar ESummary response is missing expected fields
    """

    # Validate HGVS format of variant
    if not (":" in hgvs_variant and "c." in hgvs_variant):
        raise HGVSFormatError(
            f"Invalid HGVS format: {hgvs_variant}."
            "Expected e.g. 'NM_001377265.1:c.841G>T'."
        )
    

    # Search ClinVar for variant ClinVar ID
    try:
        handle = Entrez.esearch(db="clinvar", term=hgvs_variant)  # Open connection to ClinVar and query database via Entrez ESearch using the HGVS-formatted variant
        record = Entrez.read(handle)  # Parse XML response from ESearch into a Python dictionary
        handle.close()  # Close connection
    except Exception as e:
        raise ClinVarConnectionError(f"Unable to connect to ClinVar during ESearch: {e}") from e

    if not record.get("IdList"):
        raise ClinVarIDNotFoundError(f"Variant {hgvs_variant} not found in ClinVar.")

    clinvar_id = record["IdList"][0]


    # Fetch ClinVar summary using ClinVar ID
    try:
        handle = Entrez.esummary(db="clinvar", id=clinvar_id)  # Open connection to ClinVar and query database via Entrez ESummary using the ClinVar ID
        summary = Entrez.read(handle, validate=False)  # Parse XML response from ESummary into a Python dictionary
        handle.close()  # Close connection
    except Exception as e:
        raise ClinVarConnectionError(f"Unable to connect to ClinVar during ESummary: {e}") from e

    
    # Extract key fields from ClinVar ESummary
    doc = summary["DocumentSummarySet"]["DocumentSummary"][0]

    try:
        gene_symbol = doc["genes"][0]["symbol"]
    except (KeyError, IndexError, TypeError):
        print("Gene symbol not found")
        gene_symbol = "N/A"
    
    try:
        cdna_change = doc["variation_set"][0]["cdna_change"]
    except (KeyError, IndexError, TypeError):
        print("cDNA change not found")
        cdna_change = "N/A"

    try:
        accession = doc["accession"]
    except (KeyError, IndexError, TypeError):
        print("ClinVar accession not found")
        accession = "N/A"

    try:
        classification = doc["germline_classification"]["description"]
    except (KeyError, IndexError, TypeError):
        print("ClinVar consensus classification not found")
        classification = "N/A"
    
    try:
        scv_list = doc["supporting_submissions"]["scv"]
        num_submissions = len(scv_list)
    except (KeyError, IndexError, TypeError):
        print("Number of submitted records not found")
        num_submissions = "N/A"

    try:
        review_status = doc["germline_classification"]["review_status"]
    except (KeyError, IndexError, TypeError):
        print("Review status not found")
        review_status = "N/A"

    try:
        condition_name = doc["germline_classification"]["trait_set"][0]["trait_name"]
    except (KeyError, IndexError, TypeError):
        print("Associated condition not found")
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

if __name__ == "__main__":

    hgvs_variant = "NM_001377265.1:c.841G>T"
    clinvar_output= fetch_clinvar_record(hgvs_variant)
    print(json.dumps(clinvar_output, indent=4))


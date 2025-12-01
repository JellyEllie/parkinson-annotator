"""
This script fetches HGVS nomenclature using the VariantValidator REST API.
For a given variant in the VCF-style genomic format (e.g "17:45983420:G:T"),
it returns the HGVS-formatted nomenclature for the MANE Select transcript 
(e.g. "NM_001377265.1:c.841G>T").

References:
VariantValidator REST API documentation
(https://rest.variantvalidator.org/)
"""

import json
import requests


class VariantDescriptionError(Exception):
    """Custom exception raised when the variant description string is not in the appropriate format."""
    pass


class VariantValidatorResponseError(Exception):
    """Custom exception raised when unable to connect to VariantValidator API or response lacks expected variant data."""
    pass


def fetch_variant_validator(variant_description):
    """
    This function queries the VariantValidator API to obtain HGVS nomenclature for a genomic 
    variant, using genome build GRCh38 and the MANE Select transcript.

    Parameters:
    variant_description (str): A variant in the VCF-style genomic format (e.g. "17:45983420:G:T").
 
    Returns:
    dict: A JSON response from the API.

    Raises:
    VariantDescriptionError: If the variant description does not have the expected ": format.
    requests.exceptions.RequestException: If there is an API error.
    """


    # Validate VCF-style genomic format of variant
    # Expected format: CHR:POSITION:REF:ALT
    variant_fields = variant_description.split(":")  # Splits the VCF-style format, separated by ":", and returns a list
    if len(variant_fields) != 4:
        raise VariantDescriptionError(
            f"Invalid VCF-style format: '{variant_description}'. "
            "Expected 4 colon-separated fields, e.g. '17:45983420:G:T'."
        )
    

    # Specifying API parameters: genome build and transcript
    genome_build = "GRCh38"
    select_transcripts = "mane_select"


    # Construct VariantValidator API request URL
    url = f"https://rest.variantvalidator.org/VariantValidator/variantvalidator/{genome_build}/{variant_description}/{select_transcripts}"


    # Perform GET request to VariantValidator API
    try:
        r = requests.get(url)
        r.raise_for_status()  
    except requests.exceptions.RequestException as e:
        raise VariantValidatorResponseError(f"Unable to connect to VariantValidator API: {e}") from e


    # VariantValidator response stored
    summary = r.json()


    # Identify the main variant record key
    # API response includes metadata keys ('flag', 'metadata'), to skip
    for key in summary.keys():
        if key not in ("flag", "metadata"):
            first_key = key
            break
    
    if not first_key:
        raise VariantValidatorResponseError(
            "No variant data found in VariantValidator response."
        )

    hgvs_record = summary[first_key]  # Stores main HGVS variant record


    # Extract key fields from VariantValidator response
    try:
        hgvs_mane_select = first_key
    except(KeyError, IndexError, TypeError):
        print("HGVS MANE Select nomenclature not found")
        hgvs_mane_select = "N/A"

    try:
        hgnc_id = hgvs_record["gene_ids"]["hgnc_id"]
    except(KeyError, IndexError, TypeError):
        print("HGNC ID not found")
        hgnc_id = "N/A"
    
    try:
        omim_id = hgvs_record["gene_ids"]["omim_id"]
    except(KeyError, IndexError, TypeError):
        print("OMIM ID not found")
        omim_id = "N/A"


    return {
        "HGVS nomenclature": hgvs_mane_select,
        "HGNC ID": hgnc_id,
        "OMIM ID": omim_id[0] if isinstance(omim_id, list) and omim_id else "N/A", # OMIM ID is a list, returns first item if OMIM list is present 
    }


if __name__ == "__main__":
    
    variant_description = "17:45983420:G:T"
    variant_validator_output = fetch_variant_validator(variant_description)
    print(json.dumps(variant_validator_output, indent=4))

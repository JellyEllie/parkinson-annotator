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
    """Custom exception raised when the variant descrption string is not in the appropriate format."""
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
    VariantDescriptionError: If the variant descrption does not have the expected ": format.
    requests.exceptions.RequestException: If there is an API error.
    """

    # Validate VCF-style genomic format of variant
    variant_fields = variant_description.split(":")  # Splits the VCF-style format, separated by ":", and returns a list
    if len(variant_fields) != 4:
        raise VariantDescriptionError(
            f"Invalid VCF-style format: '{variant_description}'. "
            "Expected 4 colon-separated fields, e.g. '17:45983420:G:T'."
        )
    

    # Specifying genome build and transcript
    genome_build = "GRCh38"
    select_transcripts = "mane_select"


    # Construct the API request URL
    url = f"https://rest.variantvalidator.org/VariantValidator/variantvalidator/{genome_build}/{variant_description}/{select_transcripts}"

    #Perform GET request to VariantValidator
    try:
        r = requests.get(url)
        r.raise_for_status()  
    except requests.exceptions.RequestException as e:
        raise



    # VariantValidator response stored
    try:
        summary = r.json()
    except ValueError as e:
        raise SystemExit(f"Error parsing VariantValidator response: {e}")
    


    # Find the main variant record (i.e. the first key in dictionary 'summary)
    for key in summary.keys():
        if key not in ("flag", "metadata"):
            main_key = key
            break

    record = summary[main_key]

    # Extract 3 key fields
    try:
        hgvs_mane_select = main_key
    except(KeyError, IndexError, TypeError):
        print("HGVS Mane Select nomenclature not found")
        hgvs_mane_select = "N/A"

    try:
        hgnc_id = record["gene_ids"].get("hgnc_id")
    except(KeyError, IndexError, TypeError):
        print("HGNC ID not found")
        hgnc_id = "N/A"
    
    try:
        omim_id = record["gene_ids"].get("omim_id")
    except(KeyError, IndexError, TypeError):
        print("OMIM ID not found")
        omim_id = "N/A"


    return {
        "HGVS nomenclature": hgvs_mane_select,
        "HGNC ID": hgnc_id,
        "OMIM ID": omim_id[0]
    }


if __name__ == "__main__":
    
    variant_description = "17:45983420:G:T"
    variant_validator_output = fetch_variant_validator(variant_description)
    print(json.dumps(variant_validator_output, indent=4))

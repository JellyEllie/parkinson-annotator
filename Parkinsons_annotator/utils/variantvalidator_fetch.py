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

    # Ensure input variant is a string
    if not isinstance(variant_description, str):
        raise VariantDescriptionError(
            "Variant description must be a string."
        )


    # Validate VCF-style genomic format of variant
    # Expected format: CHROM:POSITION:REF:ALT
    variant_fields = variant_description.split(":")  # Splits the VCF-style format, separated by ":", and returns a list
    if len(variant_fields) != 4:
        raise VariantDescriptionError(
            f"Invalid VCF-style format: '{variant_description}'. "
            "Expected 4 colon-separated fields, e.g. '17:45983420:G:T'."
        )
    

    # Validate that CHROM should be 1-22, X or Y
    chrom, position, ref, alt = variant_fields
    
    valid_chromosomes = ["X", "Y"] + [str(i) for i in range(1, 23)]
    if chrom not in valid_chromosomes:
        raise VariantDescriptionError(
            f"Invalid chromosome value: '{chrom}'. "
             "Expected 1-22, X or Y."
        )
    
    # Validate that POSITION should be digits only
    if not position.isdigit():
        raise VariantDescriptionError(
            f"Invalid genomic position: '{position}'. "
            "Position must be numeric."
        )
    
    # Validate that REF and ALT must be A, C, G or T
    valid_bases = ["A", "C", "G", "T"]
    if ref not in valid_bases or alt not in valid_bases:
        raise VariantDescriptionError(
            f"Invalid base(s): '{ref}>{alt}'. "
            "Reference and alternate bases must both be uppercase nucleotide letters A, C, G or T."
        )


    # Specifying API parameters: genome build and transcript
    genome_build = "GRCh38"
    select_transcripts = "mane_select"


    # Construct VariantValidator API request URL
    url = f"https://rest.variantvalidator.org/VariantValidator/variantvalidator/{genome_build}/{variant_description}/{select_transcripts}"


    # Perform GET request to VariantValidator API
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status() 
    except requests.exceptions.RequestException as e:
        raise VariantValidatorResponseError(f"Unable to connect to VariantValidator API: {e}") from e


    # VariantValidator response stored
    try:
        summary = r.json()
    except ValueError as e:
        raise VariantValidatorResponseError(
            f"Invalid JSON response from VariantValidator: {e}") from e


    # Identify the first key in the JSON response that corresponds with the HGVS transcript
    first_key = None
    for key in summary.keys():
        if ":c." in key:
            first_key = key
            break

    if not first_key:
        raise VariantValidatorResponseError(
            "VariantValidator returned no valid HGVS transcript notation."
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
        "OMIM ID": omim_id[0] if isinstance(omim_id, list) and omim_id else "N/A"  # OMIM ID is a list, returns first item if OMIM list is present 
    }


if __name__ == "__main__":  # pragma: no cover
    
    variant_description = "17:45983420:G:T"
    variant_validator_output = fetch_variant_validator(variant_description)
    print(json.dumps(variant_validator_output, indent=4))

"""
This script fetches variant information using the VariantValidator REST API.
For a given variant in the VCF-style genomic format (e.g "17:45983420:G:T"),
the script retrieves the HGVS transcript notation for the MANE Select transcript 
(e.g. "NM_001377265.1:c.841G>T"), and the corresponding HGNC and OMIM IDs.

References:
VariantValidator REST API documentation
(https://rest.variantvalidator.org/)
"""

import json
import requests
from Parkinsons_annotator.logger import logger


class VariantDescriptionError(Exception):
    """Custom exception raised when the variant description string is not in the appropriate format."""
    pass


class VariantValidatorResponseError(Exception):
    """Custom exception raised when unable to connect to VariantValidator API or response lacks expected variant data."""
    pass


def fetch_variant_validator(variant_description):
    """
    This function queries the VariantValidator API to obtain HGVS nomenclature, HGNC ID and OMIM ID
    for a genomic variant, using genome build GRCh38 and the MANE Select transcript.

    Parameters:
    variant_description (str): A variant in the VCF-style genomic format CHROM:POSITION:REF:ALT (e.g. "17:45983420:G:T").
 
    Returns:
    dict: A JSON response from the API containing: HGVS nomenclature, HGNC ID and OMIM ID

    Raises:
    VariantDescriptionError: If the variant description does not have the expected format and values.
    requests.exceptions.RequestException: If there is an API error.
    VariantValidatorResponseError: If the VariantValidator API connection failed or API response is invalid.
    """

    logger.info(f"Fetching VariantValidator information for the variant: {variant_description}.")

    # Ensure input variant is a string
    if not isinstance(variant_description, str):
        logger.error("Variant description is not a string.")
        raise VariantDescriptionError("Variant description must be a string.")


    # Validate VCF-style genomic format of variant
    # Expected format: CHROM:POSITION:REF:ALT
    variant_fields = variant_description.split(":")  # Splits the VCF-style format, separated by ":", and returns a list
    logger.debug(f"Split variant fields: {variant_fields}.")

    if len(variant_fields) != 4:
        logger.error("Variant format has incorrect number of fields.")
        raise VariantDescriptionError(
            f"Invalid VCF-style format: {variant_description}. "
            "Expected 4 colon-separated fields, CHROM:POSITION:REF:ALT e.g. '17:45983420:G:T'."
        )
    
    
    chrom, position, ref, alt = variant_fields

    # Validate that CHROM should be 1-22, X or Y
    logger.debug(f"Validating chromosome: {chrom}.")
    valid_chromosomes = ["X", "Y"] + [str(i) for i in range(1, 23)]
    
    if chrom not in valid_chromosomes:
        logger.error(f"Invalid chromosome provided: {chrom}.")
        raise VariantDescriptionError(
            f"Invalid chromosome value: '{chrom}'. Expected 1-22, X or Y."
        )
    

    # Validate that POSITION should be digits only
    logger.debug(f"Validating genomic position: {position}.")
    
    if not position.isdigit():
        logger.error(f"Position is not numeric: {position}.")
        raise VariantDescriptionError(
            f"Invalid genomic position: '{position}'. Position must be numeric."
        )
    

    # Validate that REF and ALT must be A, C, G or T
    logger.debug(f"Validating reference and alternate bases: {ref}, {alt}.")
    valid_bases = ["A", "C", "G", "T"]
    
    if ref not in valid_bases or alt not in valid_bases:
        logger.error(f"Invalid bases provided: {ref}>{alt}.")
        raise VariantDescriptionError(
            f"Invalid base(s): '{ref}>{alt}'. "
            "Reference and alternate bases must both be uppercase nucleotide letters A, C, G or T."
        )


    # Specifying API parameters: genome build and transcript
    genome_build = "GRCh38"
    select_transcripts = "mane_select"


    # Construct VariantValidator API request URL
    url = f"https://rest.variantvalidator.org/VariantValidator/variantvalidator/{genome_build}/{variant_description}/{select_transcripts}"

    logger.info(f"Querying the VariantValidator API at URL: {url}.")


    # Perform GET request to VariantValidator API
    try:
        r = requests.get(url, timeout=15)  
        r.raise_for_status()
        logger.info("VariantValidator API request is successful.")
    except requests.exceptions.RequestException as e:
        logger.error ("Connection to the VariantValidator API was unsuccessful.")
        logger.exception(e)
        raise VariantValidatorResponseError(f"Unable to connect to the VariantValidator API: {e}") from e


    # VariantValidator response stored
    try:
        summary = r.json()
    except ValueError as e:
        logger.error("VariantValidator returned invalid JSON.")
        logger.exception(e)
        raise VariantValidatorResponseError(
            f"Invalid JSON response from VariantValidator: {e}") from e


    # Identify the first key in the JSON response that corresponds with the HGVS transcript
    first_key = None
    for key in summary.keys():
        if ":c." in key:
            first_key = key
            break

    if not first_key:
        logger.error("VariantValidator response contained no ':c.' HGVS keys.")
        raise VariantValidatorResponseError(
            "VariantValidator returned no valid HGVS transcript notation."
        )
    
    logger.debug(f"HGVS transcript key identified: {first_key}.")
    hgvs_record = summary[first_key]  # Stores main HGVS variant record


    # Extract key fields from VariantValidator response
    try:
        hgvs_mane_select = first_key
    except(KeyError, IndexError, TypeError):
        logger.error("HGVS MANE Select nomenclature not found.")   # HGVS MANE Select is a key requirement, so raised as logger.error
        

    try:
        hgnc_id = hgvs_record["gene_ids"]["hgnc_id"]
    except(KeyError, IndexError, TypeError):
        logger.warning ("HGNC ID not found.")  # Some transcripts may not have HGNC ID, so raised as logger.warning
        
 
    try:
        omim_id = hgvs_record["gene_ids"]["omim_id"]
    except(KeyError, IndexError, TypeError):
        logger.warning("OMIM ID not found.")  # Some genes may not have OMIM ID, so raised as logger.warning
        
    
    logger.debug(f"Extracted HGVS nomenclature: {hgvs_mane_select}.")
    logger.debug(f"Extracted HGNC ID: {hgnc_id}.")
    logger.debug(f"Extracted OMIM ID: {omim_id}.")


    return {
        "HGVS nomenclature": hgvs_mane_select,
        "HGNC ID": hgnc_id,
        "OMIM ID": omim_id[0] if isinstance(omim_id, list) and omim_id else "N/A"  # OMIM ID is a list, returns first item if OMIM list is present 
    }


if __name__ == "__main__":  # pragma: no cover
    
    variant_description = "17:45983420:G:T"
    variant_validator_output = fetch_variant_validator(variant_description)
    print(json.dumps(variant_validator_output, indent=4))

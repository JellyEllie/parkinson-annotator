from parkinsons_annotator.modules.db import get_db_session
from parkinsons_annotator.modules.models import Variant
from parkinsons_annotator.logger import logger

# Check whether variant has been uploaded before
def existing_variant_check(vcf_form:str):
    """
    Checks whether variant already exists in database, if so, returns the variant data to allow the data extraction
    script to skip API calls.

    Args:
        vcf_form: Genomic notation of variant

    Returns:
        Dictionary of variant data

    """
    # Establish connection to database
    session = get_db_session()
    # Use get() method to retrieve variant object from database using primary key
    variant = session.get(Variant, vcf_form)

    # Return False if variant not found
    if not variant:
        return None

    # Otherwise, return variant data
    return {
        "hgvs": variant.hgvs,
        "vcf_form": variant.vcf_form,
        "clinvar_id": variant.clinvar_id,
        "classification": variant.classification,
        "gene_symbol": variant.gene_symbol,
        "cdna_change": variant.cdna_change,
        "clinvar_accession": variant.clinvar_accession,
        "num_records": variant.num_records,
        "review_status": variant.review_status,
        "associated_condition": variant.associated_condition,
        "clinvar_url": variant.clinvar_url
    }

# Check whether patient has been uploaded before, if so perform md5sum and if file has changed, reupload
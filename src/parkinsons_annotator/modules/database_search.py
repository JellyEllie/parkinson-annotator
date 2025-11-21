"""
This module performs a database search using SQLAlchemy ORM.

Functions:
    database_list: Return list of database objects matching the search criteria.
        Example: if search_type is 'variant', return list of patients with that variant.

"""

from src.parkinsons_annotator.modules.models import Variant, Patient, Connector
from src.parkinsons_annotator.logger import logger
from src.parkinsons_annotator.modules.db import get_db_session


def database_list(search_type=None, search_value=None):
    """
    Search the database based on user-specified type and value.

    Args:
        search_type (str): Type of search specified by the user.
            Determines what is returned:
                - 'variant': List of patients with matching variant.
                - 'gene_symbol': List of variants for that gene.
                - 'classification': List of variants with that classification.
                - 'patient': List of variants for that patient.
        search_value (str): Input value for the search, e.g. "NM_001377265.1:c.841G>T".

    Returns:
        list: List of query results (e.g., patient names).
    """

    # Get database session for query
    db_session = get_db_session()

    if not search_type or not search_value:
        logger.warning("Search called without search_type or search_value")
        return []

    # Based on search type, perform SQL query to return list from database
    try:
        # --- Search by variant ---
        if search_type == 'variant':

            # If input value is in HGVS format:
            if search_value.lower().startswith(("nm", "nc")):
                logger.info(f"Searching variant by HGVS: {search_value}")

                # Return list of patients with matching hgvs id
                search_results = (
                    db_session.query(Patient.name)
                    .join(Connector, Patient.name == Connector.patient_name)
                    .join(Variant, Variant.id == Connector.variant_id)
                    .filter(Variant.hgvs.ilike(search_value))
                    .all()
                )
                return [r[0] for r in search_results]

            # If input value is in genomic notation format:
            logger.info(
                f"Searching variant by genomic notation: {search_value}"
            )
            # Return list of patients with matching genomic notation
            search_results = (
                db_session.query(Patient.name)
                .join(Connector, Patient.name == Connector.patient_name)
                .join(Variant, Variant.id == Connector.variant_id)
                .filter(Variant.vcf_form.ilike(search_value))
                .all()
            )
            logger.info(f"Found {len(search_results)} patients with variant.")
            return [r[0] for r in search_results]

            # --- Other search types not yet implemented ---
            logger.info(f"Search type '{search_type}' not implemented yet.")
            return []

    except Exception as e:
        logger.error(f"Database search failed: {e}")
        return []

        # if search_type == 'gene_symbol': return all variants for that gene, with the patient name and pathogencity
        # if search_type == 'patient': return all variants for that patient, with the pathogencity
        # if search_type == 'classification': return all variants with that classification, with the patient name and pathogencity


### take variant info and return clinvar accession ID for that variant
 ### take clinvar accession ID and pass to clinvar API to get clinvar summary, and return patients

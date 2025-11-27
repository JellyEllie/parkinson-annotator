"""
This module performs a database search using SQLAlchemy ORM.

Functions:
    database_list: Return list of database objects matching the search criteria.
        Example: if search_type is 'variant', return list of patients with that variant.

Exceptions:
    SearchFieldEmptyError: Raised if search_type or search_value is empty.
    NoMatchingRecordsError: Raised if search finds no records matching the search criteria.
"""

from parkinsons_annotator.modules.models import Variant, Patient, Connector
from parkinsons_annotator.logger import logger
from parkinsons_annotator.modules.db import get_db_session

# Custom exceptions
class SearchFieldEmptyError(Exception):
    pass
class NoMatchingRecordsError(Exception):
    pass

# Search function
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

    # Raise error if no search type or value provided
    if not search_type or not search_value:
        logger.warning("Search called without search_type or search_value")
        raise SearchFieldEmptyError("Missing search fields.")

    # Based on search type, perform SQL query to return list from database
    # --- Search by variant ---
    if search_type == 'variant':
        logger.info("Searching database for variant")

        # Search in HGVS format:
        if search_value.lower().startswith(("nm", "nc")):
            logger.info(f"Searching variant by HGVS: {search_value}")

            # Find list of patients with matching hgvs id
            query = (
                db_session.query(Patient.name)
                .join(Connector, Patient.name == Connector.patient_name)
                .join(Variant, Variant.vcf_form == Connector.variant_vcf_form)
                .filter(Variant.hgvs.ilike(search_value))
            )

        # Search in genomic notation format:
        else:
            logger.info(f"Searching variant by genomic notation: {search_value}")

            # Find list of patients with matching genomic notation
            query = (
                db_session.query(Patient.name)
                .join(Connector, Patient.name == Connector.patient_name)
                .join(Variant, Variant.vcf_form == Connector.variant_vcf_form)
                .filter(Variant.vcf_form.ilike(search_value))
            )

        # Execute query and fetch results
        query_results = query.all()
        logger.info(f"Found {len(query_results)} patients with variant.")

        # Raise exception if no matching records found
        if not query_results:
            logger.info(f"No patients found with variant '{search_value}'.")
            raise NoMatchingRecordsError(f"No patients found with variant '{search_value}'.")

        # Flatten SQLAlchemy tuple into list of patient names
        return [r[0] for r in query_results]

    # --- Search by gene symbol ---
    elif search_type == 'gene_symbol':
        logger.info(f"Searching database for gene symbol= '{search_value}'")

        # Find list of variants for that gene with patient name and variant classification
        query = (
            db_session.query(
                Variant.hgvs,
                Patient.name,
                Variant.classification
            )
            .join(Connector, Connector.variant_vcf_form == Variant.vcf_form)
            .join(Patient, Patient.name == Connector.patient_name)
            .filter(Variant.gene_symbol.ilike(search_value))
        )
        query_results = query.all()
        logger.info(f"Found {len(query_results)} for gene symbol '{search_value}'")

        # Raise exception if no matching records found
        if not query_results:
            logger.info(f"No variants found with gene symbol '{search_value}'.")
            raise NoMatchingRecordsError(f"No variants found with gene symbol '{search_value}'.")

        # Flatten SQLAlchemy tuple into list of dictionaries
        return [
            {
                "hgvs": r[0],
                "patient": r[1],
                "classification": r[2]
            }
            for r in query_results
        ]

    # --- Search by patient ---
    elif search_type in ('patient', 'patient_name'):
        logger.info(f"Searching database for patient= '{search_value}'")

        # Find list of variants for that patient with the pathogencity
        query = (
            db_session.query
            (Variant.hgvs,
             Variant.gene_symbol,
             Variant.classification)
            .join(Connector, Connector.variant_vcf_form == Variant.vcf_form)
            .join(Patient, Patient.name == Connector.patient_name)
            .filter(Patient.name.ilike(f"%{search_value}%"))
        )
        query_results = query.all()
        logger.info(f"Found {len(query_results)} variants for patient '{search_value}'")

        # Raise exception if no matching records found
        if not query_results:
            logger.info(f"No variants found for patient '{search_value}'.")
            raise NoMatchingRecordsError(f"No variants found for patient '{search_value}'.")

        # Flatten SQLAlchemy tuple into list of dictionaries
        return [
            {
                "hgvs": r[0],
                "gene_symbol": r[1],
                "classification": r[2],
            }
            for r in query_results
        ]

    elif search_type == 'classification':
        logger.info(f"Searching database for classification= '{search_value}'")
        # Find list of variants with that classification
        query = (
            db_session.query
            (Variant.hgvs)
            .filter(Variant.classification.ilike(search_value))
        )

        query_results = query.all()
        logger.info(f"Found {len(query_results)} variants for classification '{search_value}'")

        # Raise exception if no matching records found
        if not query_results:
            logger.info(f"No variants found for classification '{search_value}'.")
            raise NoMatchingRecordsError(f"No variants found for classification '{search_value}'.")

        # Flatten SQLAlchemy tuple into list of dictionaries
        return [r[0] for r in query_results]

### take variant info and return clinvar accession ID for that variant
 ### take clinvar accession ID and pass to clinvar API to get clinvar summary, and return patients

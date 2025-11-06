"""
This module performs a database search using SQLAlchemy ORM.

Functions:
    database_list: Return list of database objects matching the search criteria.
        Example: if search_type is 'variant', return list of patients with that variant.

"""

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from Parkinsons_annotator.modules.models import Variant, Patient, Connector


def database_list(search_type=None, search_value=None):
    """
    Search the 'variants' table based on the 'search_type' the user selects from the Flask dropdown menu
    and the 'search_value' which is the text entered by the user.

    Args:
        search_type (str): Type of search — should match a Variant attribute
                           e.g., 'name', 'id', 'gene', 'classification'.
        search_value (str): Value to search for.

    Returns:
        list[Variant]: List of Variant objects matching the query.
    """
    # Create database engine
    engine = create_engine('sqlite:///parkinsons_data.db')  # database URL here

    # Create session for querying the database
    Session = sessionmaker(bind=engine)
    db_session = Session()


    # Based on search type, perform SQL query to find needed info
    try:
        if search_type == 'variant':
            # If input is in HGVS format:
            if search_value.startswith(("nm", "nc")):
                # Return list of patients with matching hgvs id
                search_results = (db_session.query(Patient.name)
                    .join(Connector, Patient.name == Connector.patient_name)
                    .join(Variant, Variant.id == Connector.variant_id)
                    .filter(Variant.hgvs == search_value)
                    .all()
                )
            else:
                # Placeholder for other variant-related searches
                # all non-HGVS names will be in genomic notation as input has already been validated in the search form
                # If input is in genomic notation: convert to hgvs, return all patients with that variant, and variant info table and clinvar annotation
                print("Variant search value does not appear to be an HGVS ID.")
                return []

        else:
            print(f"Search type '{search_type}' not implemented yet.")
            # if search_type == 'gene_symbol': return all variants for that gene, with the patient name and pathogencity
            # if search_type == 'patient': return all variants for that patient, with the pathogencity
            # if search_type == 'classification': return all variants with that classification, with the patient name and pathogencity

            return []

    finally:
        db_session.close()


 ### take variant info and return clinvar accession ID for that variant
 ### take clinvar accession ID and pass to clinvar API to get clinvar summary, and return patients

"""
This module performs a database search using SQLAlchemy ORM.

Functions:
    database_list: Return list of database objects matching the search criteria.
        Example: if search_type is 'variant', return list of patients with that variant.

"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from parkinsons_annotator.modules.models import Variant, Patient, Connector
from parkinsons_annotator.utils.parse_genomic_notation import parse_genomic_notation
from pathlib import Path


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

    # Create database engine
    DB_PATH = Path(__file__).resolve().parents[1] / "parkinsons_data.db"

    if not DB_PATH.exists():
        print(f"❌ Database not found at: {DB_PATH}")
        return []


    engine = create_engine(f"sqlite:///{DB_PATH}")
    print(f"Connecting to database at: {DB_PATH}")

    # Create session for querying the database
    Session = sessionmaker(bind=engine)
    db_session = Session()


    # Based on search type, perform SQL query to return list from database
    try:
        if search_type == 'variant':
            # If input value is in HGVS format:
            if search_value.startswith(("nm", "nc")):
                # Return list of patients with matching hgvs id
                search_results = (
                    db_session.query(Patient.name)
                    .join(Connector, Patient.name == Connector.patient_name)
                    .join(Variant, Variant.id == Connector.variant_id)
                    .filter(Variant.hgvs.ilike(search_value))
                    .all()
                )
                return [r[0] for r in search_results]
            else:
                # All non-HGVS names will be in genomic notation as input has already been validated in the search form
                # Parse genomic notation into chromosome, position, reference, and alternate alleles
                try:
                    chr_value, pos_value, ref_value, alt_value = parse_genomic_notation(search_value)
                except ValueError as e:
                    print(f"Invalid genomic notation: {e}")
                    return []

                # Query the database using all four fields
                results = (
                    db_session.query(Patient.name)
                    .join(Connector, Patient.name == Connector.patient_name)
                    .join(Variant, Variant.id == Connector.variant_id)
                    .filter(
                        Variant.chromosome == chr_value,
                        Variant.pos == pos_value,
                        Variant.ref == ref_value,
                        Variant.alt == alt_value
                    )
                    .all()
                )

                return [r[0] for r in results]

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

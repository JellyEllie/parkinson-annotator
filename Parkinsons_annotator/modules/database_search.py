"""
This module performs a database search in the 'variants' table using SQLAlchemy ORM.

It defines a Variant model class, connects to the database, and and allows
the user to search for variants based on patient name, variant ID, or other
fields such as gene or classification.

Example:
Run this script directly and follow the prompts to search the database:

    $ python variant_query.py

"""

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# create base class for declarative mapping
Base = declarative_base()

# define mapping class for the variant table in database
class Variant(Base):
    """
    ORM mapping for the 'variants' table in the database.

    Attributes:
        id (int): Primary key for the variant record.
        name (str): Patient name associated with the variant.
        chromosome (int): Chromosome on which the variant is located.
        pos (int): Position of the variant on the chromosome.
        ref (str): Reference allele.
        alt (str): Alternate allele.
        classification (str): Clinvar consensus classification of the variant.
        gene (str): Gene symbol associated with the variant.
    """
       
    __tablename__ = 'variants'
    id = Column(Integer, primary_key=True) # primary key column
    name = Column(String)  # patient name
    chromosome = Column(Integer)  # chromosome number
    pos = Column(Integer)  # position on chromosome
    ref = Column(String)  # reference allele
    alt = Column(String)  # alternate allele
    classification = Column(String)  # clinvar consensus classification
    gene = Column(String)  # gene symbol

    def __repr__(self):
        """
        Return a concise, human-readable string representation of a Variant.
        Returns:
        str: Formatted string with key variant information.
            """
        return (f"<Variant(name={self.name}, chr={self.chromosome}, "
                f"pos={self.pos}, ref={self.ref}, alt={self.alt})>")

# function to perform searches
def search_variants(session, patient_name=None, variant_id=None, gene=None):
    """
    Search for variants in the database based on provided criteria.

    Args:
        session (Session): SQLAlchemy session for database interaction.
        patient_name (str, optional): Patient name to filter by.
        variant_id (int, optional): Variant ID to filter by.
        gene (str, optional): Gene symbol to filter by.

    Returns:
        list: List of Variant objects matching the search criteria.
    """
    query = session.query(Variant)

    # create SQL queries using SQLAlchemy ORM filters based on provided parameters
    if patient_name:
        query = query.filter(Variant.name.ilike(f"%{patient_name}%"))
    if variant_id:
        query = query.filter(Variant.id == variant_id)
    if gene:
        query = query.filter(Variant.gene.ilike(f"%{gene}%"))

    return query.all()

if __name__ == "__main__":

    # create database engine
    engine = create_engine('sqlite:///parkinsons_data.db') # add database URL here

    # ensure tables exist in the database before running queries
    Base.metadata.create_all(engine)

    # create session for querying the database
    Session = sessionmaker(bind=engine)
    db_session = Session()

    # welcome message to user that introduces input options
    print("Welcome to the Variant Database Search!")
    print("You can currently search for variants by patient name, variant ID, or gene symbol.")

    # get user input for search criteria
    name_input = input("Enter patient name to search (or press Enter to skip): ").strip() or None
    id_input = input("Enter variant ID (or leave blank): ").strip()
    variant_id_input = int(id_input) if id_input else None
    gene_input = input("Enter gene symbol to search (or press Enter to skip): ").strip() or None

    results = search_variants(db_session,
                              patient_name=name_input, 
                              variant_id=variant_id_input,
                              gene=gene_input)
    if results:
        print(f"Found {len(results)} matching variants:")
        for variant in results:
            print(variant)
    else:
        print("No matching variants found.")

    # close session
    db_session.close()
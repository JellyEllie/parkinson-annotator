"""
models.py
Defines ORM models for the Parkinson’s Annotator database.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

# Create base class for declarative mapping
Base = declarative_base()

# Define mapping class for the variant table in database
class Variant(Base):
    """ORM mapping for the 'variants' table.
    Attributes:
        id (int): Primary key for the variant record.
        chromosome (int): Chromosome on which the variant is located.
        pos (int): Position of the variant on the chromosome.
        ref (str): Reference allele.
        alt (str): Alternate allele.
        hgvs (str): HGVS notation for the variant.
        classification (str): Clinvar consensus classification of the variant.
        gene_symbol (str): Gene symbol associated with the variant.
        clinvar_id (string): Clinvar accession ID for the variant.
        """

    __tablename__ = 'variants'
    id = Column(Integer, primary_key=True)  # primary key column
    chromosome = Column(Integer)  # chromosome number
    pos = Column(Integer)  # position on chromosome
    ref = Column(String)  # reference allele
    alt = Column(String)  # alternate allele
    hgvs = Column(String)  # hgvs notation
    classification = Column(String)  # clinvar consensus classification
    gene_symbol = Column(String)  # gene symbol
    clinvar_id = Column(String)  # clinvar accession ID

    def __repr__(self):
        """
        Return a concise, human-readable string representation of a Variant.
        Returns:
        str: Formatted string with key variant information.
        """
        return (f"<Variant(id={self.id}, chr={self.chromosome}, pos={self.pos}, "
                f"ref={self.ref}, alt={self.alt}, gene={self.gene_symbol})>")


class Patient(Base):
    """ORM mapping for the 'patients' table.
    Attributes:
        name (str): Patient name.
    """
    __tablename__ = 'patients'
    name = Column(String, primary_key=True)


class Connector(Base):
    """ORM mapping for linking patients to variants.
    Attributes:
        id (int): Primary key for the link record.
        patient_name (str): Patient name. Primary key for patient table.
        variant_id (int): Primary key for the variant record.

    """
    __tablename__ = 'patient_variant'
    id = Column(Integer, primary_key=True)
    patient_name = Column(String)
    variant_id = Column(Integer)
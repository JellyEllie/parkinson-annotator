"""
ORM models for the Parkinson’s Annotator database.

This module defines the ORM classes used by SQLalchemy to represent patients and variants in the database
and the many-to-many relationships between them.

CLasses:
    Variant: Maps to variant table which contains variant characteristics e.g. HGVS notation
    Patient: Maps to patient table containing patient names
    Connector: Maps to linking table between patient and variant table
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base

# Create base class for declarative mapping
Base = declarative_base()

class Variant(Base):
    """Represent a genetic variant in the 'variants' table."""
    __tablename__ = 'variants'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chromosome = Column(Integer, nullable=False)
    pos = Column(Integer, nullable=False)
    ref = Column(String(1), nullable=False)
    alt = Column(String(1), nullable=False)
    hgvs = Column(String)
    classification = Column(String)
    gene_symbol = Column(String)
    clinvar_id = Column(String)

    def __repr__(self):
        """Return string representation of variant object"""
        return (
            f"<Variant(id={self.id}, chr={self.chromosome}, pos={self.pos}, "
            f"ref={self.ref}, alt={self.alt}, gene={self.gene_symbol})>"
        )


class Patient(Base):
    """Represent a patient in the 'patients' table."""
    __tablename__ = 'patients'

    name = Column(String, primary_key=True)


class Connector(Base):
    """
    Represent a link between patients and variants.

    This class maps the association table 'patient_variant'
    supporting the many-to-many relationship between patients
    and genetic variants.
    """
    __tablename__ = 'patient_variant'

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_name = Column(String, ForeignKey("patients.name"), nullable=False)
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=False)

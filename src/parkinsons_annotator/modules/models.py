"""
models.py
Defines ORM models for the Parkinson’s Annotator database.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger, CHAR, Text, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base

# Create base class for declarative mapping
Base = declarative_base()

class Variant(Base):
    """ORM mapping for the 'variants' table."""
    __tablename__ = 'variants'

    # id = Column(Integer, primary_key=True, autoincrement=True)  
    # pos = Column(Integer, nullable=False)                         
    # ref = Column(String(1), nullable=False)
    # alt = Column(String(1), nullable=False)
    # hgvs = Column(String)
    # classification = Column(String)
    # gene_symbol = Column(String)
    # clinvar_id = Column(String)

    #TODO: 
    id = Column(String, primary_key=True)
    chromosome = Column(SmallInteger, nullable=False)
    position = Column(Integer, nullable=False)
    ref = Column(CHAR(1), nullable=False)
    alt = Column(CHAR(1), nullable=False)
    hgvs = Column(Text)
    classification = Column(Text)
    gene_symbol = Column(Text)
    clinvar_id = Column(Text)
    cdna_change = Column(Text)
    clinvar_accession = Column(Text)
    num_submissions = Column(Integer)
    review_status = Column(Text)
    associated_condition = Column(Text)
    clinvar_url = Column(Text)

    def __repr__(self):
        return (
            f"<Variant(id={self.id}, chr={self.chromosome}, pos={self.pos}, "
            f"ref={self.ref}, alt={self.alt}, gene={self.gene_symbol})>"
        )
#TODO: 
    # id = Column(String, primary_key=True)
    # chromosome = Column(Integer, nullable=False) SmallInteger
    # position = Column(Integer, nullable=False)
    # ref = Column(CHAR(1), nullable=False)
    # alt = Column(CHAR(1), nullable=False)
    # hgvs = Column(Text)
    # classification = Column(Text)
    # gene_symbol = Column(Text)
    # clinvar_id = Column(Text)
    # cdna_change = Column(Text)
    # clinvar_accession = Column(Text)
    # num_submissions = Column(Integer)
    # review_status = Column(Text)
    # associated_condition = Column(Text)
    # clinvar_url = Column(Text)

class Patient(Base):
    """ORM mapping for the 'patients' table."""
    __tablename__ = 'patients'

    name = Column(String, primary_key=True)


class Connector(Base):                           
    """ORM mapping for linking patients to variants."""
    __tablename__ = 'patient_variant'

    # id = Column(Integer, primary_key=True, autoincrement=True)
    patient_name = Column(String, ForeignKey("patients.name"), nullable=False)
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('patient_name', 'variant_id'),
    )

"""
models.py
Defines ORM models for the Parkinson’s Annotator database.
"""

from sqlalchemy import Column, Integer, ForeignKey, VARCHAR
from sqlalchemy.orm import declarative_base

# Create base class for declarative mapping
Base = declarative_base()

class Genes(Base):
    """ORM mapping for the 'genes' table."""
    __tablename__ = 'genes'

    gene_symbol = Column(VARCHAR(10), primary_key=True)
    gene_url = Column(VARCHAR(500))

    def __repr__(self):
        return (
            f"<Gene(gene={self.gene_symbol})>"
        )

class Variant(Base):
    """ORM mapping for the 'variants' table."""
    __tablename__ = 'variants'

    vcf_form = Column(VARCHAR(30), primary_key=True) # Use genomic notation as primary key
    hgvs = Column(VARCHAR(50))
    clinvar_id = Column(VARCHAR(20))
    gene_symbol = Column(VARCHAR(10), ForeignKey("genes.gene_symbol"))
    classification = Column(VARCHAR(50))
    cdna_change = Column(VARCHAR(20))
    clinvar_accession = Column(VARCHAR(20))
    num_records = Column(VARCHAR(10))
    review_status = Column(VARCHAR(50))
    associated_condition = Column(VARCHAR(50))
    clinvar_url = Column(VARCHAR(500))

    def __repr__(self):
        return (
            f"<Variant(hgvs={self.hgvs}, gene={self.gene_symbol})>"
        )

class Patient(Base):
    """
    ORM mapping for the 'patients' table.
    Can be expanded in future to include more patient metadata.
    """
    __tablename__ = 'patients'

    name = Column(VARCHAR(15), primary_key=True)

    def __repr__(self):
        return (
            f"<Patient(name={self.name})>"
        )

class Connector(Base):
    """ORM mapping for linking patients to variants."""
    __tablename__ = 'patient_variant'

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_name = Column(VARCHAR(15), ForeignKey("patients.name"), nullable=False)
    variant_vcf_form = Column(VARCHAR(50), ForeignKey("variants.vcf_form"), nullable=False)

    def __repr__(self):
        return (
            f"<Connection(name={self.patient_name}, hgvs={self.variant_vcf_form})>"
        )
"""
this script is to create the database and the headings for the tables to be populated with the patient data
Data types:
    TEXT: Allows for characters of any length.
    INTEGER: A whole number of any length.
    CHAR(1): Single-character field.
Other database parameters:
    NOT NULL: Field must contain a value.
    AUTOINCREMENT: Automatically generates unique IDs for each record.
    PRIMARY KEY: Used to uniquely identify each record and potentially link tables.
"""


import sqlite3
from pathlib import Path

def generatetable():
    """Create the database and tables if they don't already exist."""
    db_path = Path(__file__).resolve().parents[1] / "parkinsons_data.db"
    # creates the database. this function is also used to open the database if it already exists
    conn = sqlite3.connect(db_path)
    # creates a cursor object to be able to execute SQL commands
    cur = conn.cursor()

    # Creating variants table
    # The first word is the name of the column, the second is the data type. Datatype explained above.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            name TEXT NOT NULL PRIMARY KEY
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vcf_form VARCHAR(30),
            hgvs VARCHAR(50),
            clinvar_id INTEGER,
            gene_symbol VARCHAR(10),
            classification VARCHAR(50),
            cdna_change VARCHAR(20),
            clinvar_accession VARCHAR(20),
            num_records INTEGER,
            review_status VARCHAR(50),
            associated_condition VARCHAR(50),
            clinvar_url VARCHAR(500)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patient_variant (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            variant_id INTEGER NOT NULL
        )
    """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS genes (
                    gene_symbol VARCHAR(10) PRIMARY KEY,
                    gene_link VARCHAR(500)
                )
                """)
    # Save (i.e. commit) changes
    conn.commit()
    conn.close()



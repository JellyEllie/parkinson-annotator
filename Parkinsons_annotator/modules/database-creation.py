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
            chromosome INTEGER NOT NULL,
            pos INTEGER NOT NULL,
            ref CHAR(1) NOT NULL,
            alt CHAR(1) NOT NULL,
            hgvs TEXT,
            classification TEXT,
            gene_symbol TEXT,
            clinvar_id TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patient_variant (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            variant_id INTEGER NOT NULL
        )
    """)

    # Save (i.e. commit) changes
    conn.commit()
    conn.close()

# When up and running, won't be needed as wil be called in a different script
# Main execution
db_path = Path(__file__).resolve().parents[1] / "parkinsons_data.db"

if not db_path.exists():
    generatetable()


# opens link to the database, the same as seen in the function
conn = sqlite3.connect(db_path)
# creates  a cursor object to be able to execute SQL commnds
cur = conn.cursor()

# Add testing data
patient_data = [("patient1",), ("patient2",), ("patient3",)]
variant_data = [
    (15, 38920, "A", "T", "nm_022089.4:c.1544C>T"),
    (7, 12345, "G", "C", "nm_123456.7:c.876G>C")
]
combined = [("patient1", 1), ("patient2", 1), ("patient3", 2)]


# to prevent the testing data to be input everytime this code is run. Change "stop" to "go" to fill in data
testing = "go"
if testing == "go":
    cur.executemany(
        "INSERT INTO variants (chromosome, pos, ref, alt, hgvs) VALUES (?, ?, ?, ?, ?)",
        variant_data
    )
    cur.executemany("INSERT INTO patients (name) VALUES (?)", patient_data)
    cur.executemany(
        "INSERT INTO patient_variant (patient_name, variant_id) VALUES (?, ?)",
        combined
    )
# save the changes made
conn.commit()

# Verify
cur.execute("""
    SELECT * FROM patients
    JOIN patient_variant ON patients.name = patient_variant.patient_name
    JOIN variants ON patient_variant.variant_id = variants.id
""")
for row in cur.fetchall():
    print(row)

# close the connection to the database
conn.close()

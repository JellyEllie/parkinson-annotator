"""
Creates and populates the Parkinson’s Annotator database.
"""

import sqlite3
from pathlib import Path

def generatetable():
    """Create the database and tables if they don't already exist."""
    db_path = Path(__file__).resolve().parents[1] / "parkinsons_data.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create tables
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

    conn.commit()
    conn.close()


# Main execution
db_path = Path(__file__).resolve().parents[1] / "parkinsons_data.db"

if not db_path.exists():
    generatetable()

# Add testing data
conn = sqlite3.connect(db_path)
cur = conn.cursor()

patient_data = [("patient1",), ("patient2",), ("patient3",)]
variant_data = [
    (15, 38920, "A", "T", "nm_022089.4:c.1544C>T"),
    (7, 12345, "G", "C", "nm_123456.7:c.876G>C")
]
combined = [("patient1", 1), ("patient2", 1), ("patient3", 2)]

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

conn.commit()

# Verify
cur.execute("""
    SELECT * FROM patients
    JOIN patient_variant ON patients.name = patient_variant.patient_name
    JOIN variants ON patient_variant.variant_id = variants.id
""")
for row in cur.fetchall():
    print(row)

conn.close()

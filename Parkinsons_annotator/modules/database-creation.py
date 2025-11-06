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


# import sqlite and os to usue those modules to create the database
import sqlite3
import os

# creating a function so that the code only runs when required and not every time
def generatetable():
    """ creates the database and the variants table within it, if the database does not already exist """

    # creates the database. this function is also used to open the database if it already exists
    conn = sqlite3.connect("parkinsons_data.db")

    # creates a cursor object to be able to execute SQL commands
    cur = conn.cursor()

    # creating variants table to input data into.
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
    # save the changes made aka you commit to those changes
    conn.commit()


    # close the connectionto the database
    conn.close()

# creating a variable for the database to call in the next section
db_path = "parkinsons_data.db"

# checks to see if the database exists, to create it if it doesn't
if os.path.exists(db_path):
    pass
else:
    generatetable()

# the below code is all to generate test data to use for the search testing. Can be deleted when input module is running

# opens link to the database, the same as seen in the function
conn = sqlite3.connect("parkinsons_data.db")

# creates  a cursor object to be able to execute SQL commnds
cur = conn.cursor()

# adding testing data
patient_data = [
    ("patient1",),
    ("patient2",),
    ("patient3",)
    ]
variant_data = [
    (15, 38920, "A", "T", "NM_022089.4:c.1544C>T"),
    (7, 12345, "G", "C", "NM_123456.7:c.876G>C")
]

combined = [
    ("patient1", 1),
    ("patient2", 1),
    ("patient3", 2)
]


# to prevent the testing data to be input everytime this code is run. Change "stop" to "go" to fill in data
testing = "go"
if testing == "go":
    cur.executemany(
     "INSERT INTO variants (chromosome, pos, ref, alt, hgvs) VALUES (?, ?, ?, ?, ?)", 
     variant_data)
    cur.executemany(
        "INSERT INTO patients (name) VALUES (?)", 
        patient_data)
    cur.executemany(
        "INSERT INTO patient_variant (patient_name, variant_id) VALUES (?, ?)", 
        combined)
# save the changes made
conn.commit()

# testing table
cur.execute(
    "SELECT * " \
    "FROM patients " \
    "JOIN patient_variant ON patients.name = patient_variant.patient_name " \
    "JOIN variants ON patient_variant.variant_id = variants.id")
rows = cur.fetchall()
for row in rows:
    print(row)

# close the connection to the database
conn.close()
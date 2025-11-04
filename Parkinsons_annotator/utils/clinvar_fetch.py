"""
This script uses the Biopython Entrez module to query the ClinVar NCBI database.
For a genetic variant, it retrieves annotation information (e.g. consensus classification, star rating,
associated conditions, and supporting evidence??) and returns the data in a structured format.
"""


from Bio import Entrez    #Import Entrez module from Biopython for NCBI queries
import json

Entrez.email = "naima.abdi@postgrad.manchester.ac.uk"   #Set email (required by NCBI Entrez API)


class ClinvarError(Exception):
    """Custom exception for ClinVar-related errors."""
    pass




hgvs_variant = 'NM_001377265.1:c.841G>T'    #Defining the HGVS variant string to search for

#Open a connection to ClinVar, search the ClinVar database for entries matching the HGVS variant
handle = Entrez.esearch(db='clinvar', term=hgvs_variant)    #Opens a connection to ClinVar, using the HGVS-formatted variant 
record = Entrez.read(handle)                                #Entrez.read(handle) reads the search result, and pases the XML response from NCBI and converts it into Python dictionary stored in 'record'
handle.close()                                              #Closes the handle/connection (handle = the connection that's opened when making request to NCBI API)


#'record' is a Python dictionary with many keys
#One of the keys for the dictionary is 'IdList'
print (record["IdList"])                          #Prints the ClinVar ID number as a value from the dictionary, but in list format

#Checks if 'IdList' is empty, if so raises custom error indicating that variant was not found in ClinVar
if not record["IdList"]:
    raise ClinvarError(f"Variant {hgvs_variant} not found in ClinVar.")

#Below stores the value 'record["IdList"]' into a variable called 'cinvar_id'
id_list = record["IdList"]           
print (id_list)                 #prints the ClinVar ID in a list e.g. ['578075']

clinvar_id = id_list[0]
print (clinvar_id)              #prints the clinvar_id as a string output, because its the first and only item in the 'record["IdList"]' e.g. 578075



#Open a connection to ClinVar, use esummary and ClinVar ID to get summary
handle = Entrez.esummary(db="clinvar", id=clinvar_id)        #Opens a connection to ClinVar, use esummary and ClinVar ID to get summary
summary = Entrez.read(handle, validate=False)                                #Entrez.read(handle) reads the summary response, then store this in 'summary
handle.close()                                               #Closes the handle/connection

print(summary)




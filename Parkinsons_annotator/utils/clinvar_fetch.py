"""
This script uses the Biopython Entrez module to query the ClinVar NCBI database.
For a given variant, it retrieves annotation information (e.g. classification, review status, associated condition).
"""


from Bio import Entrez    #Import Entrez module from Biopython for NCBI queries

import json


class HGVSFormatError(Exception):
    """Raised when the HGVS variant string is not in the correct format."""
    pass


class ClinVarConnectionError(Exception):
    """Raised when unable to connect to the NCBI ClinVar API e.g. during ESearch or ESummary."""
    pass


class ClinVarIDNotFoundError(Exception):
    """Raised when there is no ClinVar ID for the given variant."""
    pass


class ClinVarESummaryError(Exception):
    """Raised when the ClinVar ESummary response is missing expected fields."""
    pass


Entrez.email = "naima.abdi@postgrad.manchester.ac.uk"   #Set email (required by NCBI Entrez API)

hgvs_variant = 'NM_001377265.1:c.841G>T'    #Defining the HGVS variant string to search for


#Validate HGVS format of variant
if not (":" in hgvs_variant and "c." in hgvs_variant):
    raise HGVSFormatError(f"Invalid HGVS format: {hgvs_variant}. Expected e.g. 'NM_001377265.1:c.841G>T'.")



#Open a connection to ClinVar, search the ClinVar database for entries matching the HGVS variant
try: 
    handle = Entrez.esearch(db="clinvar", term=hgvs_variant)    #Opens a connection to ClinVar, using the HGVS-formatted variant 
    record = Entrez.read(handle)                                #Entrez.read(handle) reads the search result, and pases the XML response from NCBI and converts it into Python dictionary stored in 'record'
    handle.close()                                              #Closes the handle/connection (handle = the connection that's opened when making request to NCBI API)

except Exception as e:
    raise ClinVarConnectionError(f"Unable to connect to ClinVar during ESearch: {e}")


#'record' is a Python dictionary with many keys
#One of the keys for the dictionary is 'IdList'
# Validate that ClinVar returned at least one ID for the given variant, if IdList is empty raise error indicating that variant was not found in ClinVar
if not record.get("IdList"):
    raise ClinVarIDNotFoundError(f"Variant {hgvs_variant} not found in ClinVar.")

#If above validation passes, print the ClinVar ID
print(record.get("IdList"))


#Below stores the value 'record["IdList"]' into a variable called 'cinvar_id'
id_list = record.get("IdList")         
clinvar_id = id_list[0]
print(clinvar_id)              #prints the clinvar_id as a string output, because its the first and only item in the 'record["IdList"]' e.g. 578075



#Open a connection to ClinVar, use esummary and ClinVar ID to get summary
try:
    handle = Entrez.esummary(db="clinvar", id=clinvar_id)        #Opens a connection to ClinVar, use esummary and ClinVar ID to return a summary in XML format from NCBI API
    summary = Entrez.read(handle, validate=False)                #Entrez.read(handle) reads the summary response, parses the XML reponse into a Python object, then store this in 'summary'
    handle.close()                                               #Closes the handle/connection

except Exception as e:
    raise ClinVarConnectionError(f"Unable to connect to ClinVar during ESummary: {e}")


#Prints the entire 'summary'
print(summary)                         #This prints a nested dictionary of 'summary'

#Prints the entire 'summary' in a readable JSON format
print(json.dumps(summary, indent=4))


#Acessing specific fields in the summary response
try: 
    gene_symbol = summary['DocumentSummarySet']['DocumentSummary'][0]['genes'][0]['symbol']                                       #prints Gene symbol
    cdna_change = summary['DocumentSummarySet']['DocumentSummary'][0]['variation_set'][0]['cdna_change']                           #prints HGVS cDNA change
    accession = summary['DocumentSummarySet']['DocumentSummary'][0]['accession']                                                   #prints ClinVar Accession
    classification = summary['DocumentSummarySet']['DocumentSummary'][0]['germline_classification']['description']                 #prints the aggregate ClinVar consensus classification (e.g. "Conflicting classifications of pathogenicity"), which reflects all submitter interpretations
    review_status = summary['DocumentSummarySet']['DocumentSummary'][0]['germline_classification']['review_status']                #prints Review status
    condition_name = summary['DocumentSummarySet']['DocumentSummary'][0]['germline_classification']['trait_set'][0]['trait_name']  #prints Associated condition 

except Exception as e:
    raise ClinVarESummaryError (f"Missing expected field in ClinVar ESummary response: {e}")



print("Gene symbol:", gene_symbol)
print("cDNA chnage:", cdna_change)
print("ClinVar Accession:", accession)
print("ClinVar consensus classification:", classification)
print("Review status:", review_status)
print("Associated condition:", condition_name)




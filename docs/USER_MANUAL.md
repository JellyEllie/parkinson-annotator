# User Manual

## Starting Up
When the program starts, it should open to the search page, if it doesn't there
is a button in the top left-hand corner
![search button](manual_images/SearchButton.png) 
which directs to the search page.

## Uploading    Data
In the top right-hand corner of the page is the upload button. Both vcf and csv
files are accepted and the file name is taken as the patient name. Multiple
files can be uploaded at once by selecting multiple files in the browse section.
When the upload button is pressed it will grey out to prevent repeat pressing,
and text next to the button will it is loading. This process will take several
seconds, due to the process with which the database is filled. The program
utilises APIs to search VariantValidator and ClinVar to retrieve the necessary
information, which is then stored in the database. Whilst this process makes the
uploading of data into the database slow, it means that the search function will
be quick.

The upload function has built in checks, to ensure that if the same patient
data is uploaded twice, then the data won't be duplicated. If this happens a
pop-up will appear explaining this:

![failed upload](docs/manual_images/PatientAlreadyExists.png)

If the patient data being uploaded is no in the database, then once it has
been uploaded a pop-up will appear explaining this:

![successful upload](docs/manual_images/UploadSuccessful.png)

## Searching the Dataset

The search function will only work if a category is selected. This tells the
function where it should search and what information should be returned.
These categories are: Variant, Gene Symbol, Patient Name, and Classification. A
brief overview of what input should be given for each search and what is output
is given below the search bar on the search page.

When variant, gene symbol or patient name is selected, type or paste in the
search box, then click search or press enter.

If classification is selected, the search bar will be replaced with a second
drop-down menu, which contains the following options: Pathogenic, Likely
Pathogenic, Benign, Likely Benign, Uncertain Significance, Conflicting, Not
Provided, Not Found in Clinvar.

## Details of each search category

### Variant
**Input:** type or paste vcf (e.g. 17:44349216:A:G) or HGVF (e.g.
NM_000345.4:c.247G>C) format into the search-bar. The input is NOT
case-sensitive, but does have to be exactly correct in terms of values,
otherwise the search will return 'No matching records found'.

**Output:** the first text will re-state the search made ('Patients with
variant *searchtext*:'). Below this will be a list of all the patients in the
dataset with that variant. Below that will be the header 'Variant Information'
and below that a table showing all the ClinVar information stored within the
database:
+ Associated condition
+ ClinVar accession - the unique value for that variant that ClinVar stores and
is used by the API to search in ClinVar to gather the other information
+ ClinVar consensus classification
+ ClinVar record URL - link to ClinVar page for that variant
+ ClinVar variant ID
+ Gene Symbol
+ Genomic notation - the vcf format for the variant, adapted from the uploaded
data file
+ HGVS notation
+ Number of submitted records
+ Review status - gives an indication of how confident ClinVar is in the
classification given
+ cDNA change

Example:<br>
![variant search example](docs/manual_images/VariantSearch.png)

### Gene Symbol
**Input:** gene symbol, searching the gene name or other variation won't yield
any results. The search is NOT case-sensitive.

**Output:** the first text will re-state the search made (Patient variants
found in gene *searchtext*). Below will be a table which includes all patients
and their variants (in HGVS format) found in that gene, plus its classification.

Example:<br>
![gene symbol search example](docs/manual_images/GeneSearch.png)

### Patient Name
**Input:** the name of the patient as it is in the uploaded datafile. To see
all patients in the dataset type or paste 'patient' into the search-bar. The
search is NOT case-sensitive.

**Output:** the first text will re-state the search made (Variants identified in
*searchtext*). Below will be a table showing all variants for that patient (in
HGVS format), the classification and gene found each variant is found in.<br>
If the search is for all patients, the the first text will be 'Variants found in
all patients', with all variants in the database being listed vin the resulting
table.

Example:<br>
![patient name search example](docs/manual_images/PatientSearch.png)

### Classification
**Input:** Select a classification from list in drop-down menu.

**Output:** the first text will re-state the search made (Patient variants with
ClinVar classification: *searchtext*). If the classification selected is 'Not
Found in Clinvar', the first text will read 'Patient variants which were not
identified in ClinVar:'. Below will show a single column table showing all
variants in the database with that classification in HGVS format.

Examples:<br>
![successful classification search example](docs/manual_images/PathogenicSearch.png)
![unsuccessful classification search example](docs/manual_images/NotInClinvar.png)

## Troubleshooting
The most likely issue to occur is the a search returning nothing when it is
expected to return results. If necessary it is possible to directly view the
folder where the uploaded files are stored.

If the program is run using docker, then the uploaded files are stored:<br>
PATH LOCATION HERE

If the program is run without using docker, then the files are stored:<br>
parkinson-annotator/sr/parkinson_annotator/instance/uploads

The instance folder in one that is created by the program, so does not exist
before the program is run for the first time. This so that the database and
interactive elements are created locally to allow for secure data storage and
consistent interaction. So if the instance folder doesn't exist, run the
program to create these folders.

Other search functions can be used to ensure the correct search input is used
by copying data from those searches to paste into the search-bar. For example,
if a variant is known in patient1, but searching that variant in a variant
search yields no results. To ensure that what is being searched is exactly
correct to as it is in the database, a patient search can be done for patient1
and copy that variant from the results. This can be pasted into the search bar
for the variant search, which should then show correct results.
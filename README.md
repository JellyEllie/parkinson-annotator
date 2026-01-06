# $\color{rgba(255,0,0, 0.4)}\Huge{\textsf{Parkinson Annotator}}$
# Parkinson Annotator

### Description:  
The Parkinson Annotator project is a web-based application designed to help researchers and clinicians **upload, explore, and query** patient genomic data. This tool allows users to upload VCF and CSV files containing patient variant data and provides an **interactive interface** for searching by patient, variant, gene or pathogenicity. The results include relevant annotations and ClinVar information, making it easier for researchers and clinicians to analyse large scale patient genomic data.

### Milestones:(DISCUSS:to rid of? add screenshot image of web interface here instead) 
- Extract data from various input files
- Create backend database and load data 
- Incorporate Variant Validator and Clinvar API 
- Create frontend search function for querying data


### ✨ Features
- Upload patient data in VCF and CSV formats.
- Store and manage variant data in a local SQLite database
- Provides a light-weight flask-based web application
- Dockerised deployment for reproducible, platform-independent execution
- Search variants by:
   - HGVS symbol
   - Genomics notation
   - Gene
   - Pathogenicity classification
   - Patient name
- Retrieves external data from:
   - Clinvar
   - Variant Validator 
 
---

## 📑 Table of Contents

#### :o: &nbsp;&nbsp;&nbsp; [**Installation and usage**](#-installation-and-usage)
#### :o: &nbsp;&nbsp;&nbsp; [**Tools and dependencies**](#%EF%B8%8F-tools-and-dependencies)
#### :o: &nbsp;&nbsp;&nbsp; [**Pipeline**](#-pipeline-architecture)
#### :o: &nbsp;&nbsp;&nbsp; [**File Structure**](#-file-structure)
#### :o: &nbsp;&nbsp;&nbsp; [**Data**](#-data)
#### :o: &nbsp;&nbsp;&nbsp; [Development and testing](#-development-and-testing)
#### :o: &nbsp;&nbsp;&nbsp; [**License**](#-license)

---

## 📚 Installation and usage instructions

This project is designed to run in a **Conda environment** on **Linux Ubuntu (insert version) LTS (Jammy Jellyfish)** and is also **containerised using Docker** for easier deployment.

### 1. Clone the repository
   ```
   git clone https://github.com/JellyEllie/parkinson-annotator.git
   cd parkinson-annotator
   ```
### 2. Installing the application:  

**Option 1: Local installation (source)**

Instructions for installing and running the application from source on your local machine are provided in the [installation manual](INSTALLATION.md). This step-by-step guide walks through setting up the required environment configurations and dependencies for local development and execution.

**Option 2: Docker installation (recomennded)**

Instructions for building and running the application using Docker are provided separately in the [Docker manual](DOCKER.md). This guide covers containerised installation and execution, for a reproducible runtime environment without manual dependency setup. 

### 3. Running the application: 

Instructions on starting the application are provided in the [installation manual]((INSTALLATION.md)) and [Docker manual]((DOCKER.md)). 
Detailed intructions on how to run and use the application are provided in the [user manual](USER_MANUAL.md).

## 🛠️ Tools and dependencies

- **Flask:**  
Flask is a lightweight Python web framework used to build the interactive web interface of the Parkinsons Data Annotator. It handles routing, data uploads, and rendering HTML templates. The documentation can be found [here](https://flask.palletsprojects.com/en/stable/).

- **SQLite:**  
SQLite is a lightweight, file-based relational database used to store patient and variant data. It allows for simple and faster querying and data storage without the need for a separate database server. The documentation can be found [here](https://sqlite.org/docs.html).

- **Clinvar API:**  
The ClinVar API provides access to public variant data and pathogenicity annotations. The application queries this API to fetch up-to-date information about genomic variants. Documentation can be found [here](https://www.ncbi.nlm.nih.gov/clinvar/docs/maintenance_use/#api).

- **Variant Validator API:**  
Variant Validator is an API used to validate and standardise genomic variant notation (HGVS, VCF formats). It ensures accurate input for searching and annotation. The documentation can be found [here](https://rest.variantvalidator.org).

- **Docker:**  
Docker is used to containerise the application, ensuring consistent deployment and development environments. It allows the app to run without manual setup of Python packages or system dependencies. The documentation can be found [here](https://docs.docker.com).


## 💡 Pipeline architecture

[!image](pipeline.svg)

## 📂 File structure

TODO: To insert layout with short file descriptions - this aids users in understanding and navigating the file structure of this project.  

## 🧬 Data

The Parkinson Annotator processes patient-specific genomic variant data.
Supported formats: VCF, CSV
Input assumption: Each file representing a single patient (e.g., `patient1.vcf`, `patient2.csv`). 

- **Example file structure:**  
  Each VCF or CSV file contains variant information with columns:

| #CHROM |   POS    | ID | REF | ALT |
| :----: | :------: | :-: | :-: | :-: |
|   17   | 45983420 |  .  |  G  |  T  |


## 🔨 Development and testing

This project includes supporting documentation for developers who wish to understand or modify the codebase. Full technical details including development environment setup, logging, testing, and CI/CD are provided in the [technical manual](TECHNICAL_MANUAL.md).
- **Coding standards and best practices** The project follows standard PEP-8 standards and flask best practice; using logging for traceability, and automated testing using `pytest`.
- **CI/CD** Continuous integration is implemented using Jenkins, with the pipeline defined in the Jenkinsfile

## 📜 License
This project is licensed under the [MIT License](LICENSE).

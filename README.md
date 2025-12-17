# $\color{rgba(255,0,0, 0.4)}\Huge{\textsf{Parkinson's Data Annotator}}$

### Description:  
The Parkinsons Data Annotator is a web-based application designed to help researchers and clinicians **upload, explore, and query** patient genomic data. This tool allows users to manage VCF and CSV files containing patient variant data and provides an **interactive interface** for searching by patient, variant, or pathogenicity(insert list of al lsearch types). The results include relevant annotations and ClinVar information, making it easier for researchers and clinicians to analyse genomic data efficiently.

### Milestones:
- Extract data from various input files
- Create backend database and load data 
- Incorporate Variant Validator and Clinvar API 
- Create frontend search function for querying data 
---

## 📑 Table of Contents

#### :o: &nbsp;&nbsp;&nbsp; [**Installation**](#-installation-and-usage-instructions)
#### :o: &nbsp;&nbsp;&nbsp; [**Tools and dependencies**](#%EF%B8%8F-tools-and-dependencies)
#### :o: &nbsp;&nbsp;&nbsp; [**Pipeline**](#-pipeline-architecture)
#### :o: &nbsp;&nbsp;&nbsp; [**File Structure**](#-file-structure)
#### :o: &nbsp;&nbsp;&nbsp; [**Data**](#-data)
#### :o: &nbsp;&nbsp;&nbsp; [**License**](#-license)

---

## 📚 Installation and usage instructions
TODO: *Caitlin can fill in the step-by-step instructions as needed.*

This project is designed to run in a **Conda environment** on **Linux Ubuntu (insert version) LTS (Jammy Jellyfish)** and is also **containerised using Docker** for easier deployment.

- If the installation instructions are short, they can be included here directly.  
- Otherwise, this section can signpost detailed setup guides, specifying the recommended order for installation and configuration.

Outdated instructions (*Caitlin edit as needed*):
1. Set up conda environment
   ```
   conda env create -f environment.yml
   conda activate parkinsons-env
   conda env update --name parkinsons-env --file environment.yml --prune
   ```
2. Install pip packages
   `pip install -r requirements.txt`
3. Setup env file
   `cp .env.example .env`
   Fill out .env from supplied credentials
4. Run application
   ```
   cd Parkinsons_annotator
   python main.py
   ```

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

TODO: Insert diagram here - find draw.io diagram and insert into docs/media folder and link it here.

## 📂 File structure

TODO: To insert layout with short file descriptions - this aids users in understanding and navigating the file structure of this project.  

## 🧬 Data

The Parkinsons Data Annotator processes genomic data for Parkinson’s patients. The application supports **VCF and CSV** file formats, with each file representing a single patient (e.g., `patient1.vcf`, `patient2.csv`).

- **File structure:**  
  Each VCF or CSV file contains variant information with columns such as:

| #CHROM |   POS    | ID | REF | ALT |
| :----: | :------: | :-: | :-: | :-: |
|   17   | 45983420 |  .  |  G  |  T  |

## 📜 License
This project is licensed under the [MIT License](LICENSE).

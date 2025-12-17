# Technical Manual

## Project Overview

Parkinson’s Annotator is a Python-based software application developed to support Clinical Scientists in the annotation of genetic variants associated with Parkinson’s disease. The system allows users to upload, process and query variant data through a web-based interface.

The application integrates external variant resources (e.g. VariantValidator and ClinVar) to retrieve clinically relevant variant information. It is implemented as a Flask web application, with SQLAlchemy used for database management, and bioinformatic tools and resources for data extraction (e.g. NCBI Entrez), supported by custom utility modules (e.g. clinvar_fetch.py, variantvalidator_fetch.py).

## Installation

The instructions for setting up the development environment, installing dependencies, and configuring the project can be found in [INSTALLATION.md](./INSTALLATION.md).

## Project Structure

This project is organised as follows:

```
parkinson-annotator/
├── docs/  # Project documentation 
│   ├── DOCKER.md
│   ├── INSTALLATION.md
│   ├── TECHNICAL_MANUAL.md
│   ├── USER_MANUAL.md
│   └── index.md
├── src/
│   ├── logs/
│   │   └── parkinsons_annotator.log  # Not tracked by git           
│   └── parkinsons_annotator/
│       ├── modules/
│       │   ├── data_extraction.py
│       │   ├── database_search.py
│       │   ├── db.py
│       │   ├── models.py
│       │   └── routes.py
│       ├── templates/
│       │   ├── base.html
│       │   ├── info.html
│       │   └── interface_package.html
│       ├──  utils/
│       │   ├── clinvar_fetch.py
│       │   ├──  data_checks.py
│       │   └── variantvalidator_fetch.py
│       ├── logger.py
│       └── main.py
├── tests/
├── uploads/
├── Dockerfile                        # Instructions for building a Docker image of the application
├── Jenkinsfile                       # Defines CI pipeline 
├── README.md  
├── environment.yml                   # Conda environment specification for dependencies
├── jenkins_pipeline_console_log.txt  # CI build log
├── mkdocs.yml                        # MkDocs documentation configuration file
├── pyproject.toml                    # Python project metadata and dependencies.
└── running_main.pdf                  # Demonstration output / assignment evidence
```

- **tests/**: Unit tests (e.g. test_clinvar_fetch.py, test_data_checks.py, test_data_extraction.py, test_database_search.py, test_db.py, test_main.py, test_routes.py, test_variantvalidator_fetch.py).
- **uploads/**: Directory for user-uploaded files.

## Configuration (move to Installation.md?)

The application configuration is managed through environment variables. To initialise these settings, copy the provided `.env.example` file and rename it to `.env`, then populate it with the required values:

```sh
cp .env.example .env
```

The primary configuration options include:

- `DB_NAME`: Specifies the name of the SQLite database file (default: parkinsons_data.db)
- `ENTREZ_EMAIL`: Specified the email address required for access to the NCBI Entrez API

Additional configuration options can be set in the `.env` file.

## Running the Application (move to Installation.md?)

To set-up and run the application locally:

```sh
# Create the Conda environment
conda env create -f environment.yml

# Activate the environment 
conda activate parkinsons-env

# Start the Flask application from the project root
parkinsons-annotator
```

The application will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000).

For Docker-based deployment, see [DOCKER.md](./DOCKER.md).

## Testing (add instruction for checking coverage reports in Codecov?)

Automated tests are located in the `tests/` directory, and use the `pytest` framework.

> **Note:** The testing and coverage dependencies (`pytest`, `pytest-cov`) are not installed by default with `conda env create -f environment.yml`. Developers must install these optional dependencies separately:
>
> ```
> pip install -e '.[dev]'
> ```
>
> This will install all packages listed under `[project.optional-dependencies].dev` in the `pyproject.toml`.

To run all tests with coverage:

```sh
# Activate your Conda environment
conda activate parkinsons-env

# Install the testing and coverage dependencies (pytest, pytest-cov)
pip install -e '.[dev]'

# Navigate to the tests/ directory and run the tests with the coverage report 
cd tests
pytest --cov=parkinsons_annotator
```
Test coverage reports are displayed in the terminal. 
Add new tests in the `tests/` directory.








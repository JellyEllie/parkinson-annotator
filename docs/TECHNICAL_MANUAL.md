# Technical Manual

## Project Overview

Parkinson’s Annotator is a Python-based software application developed to support Clinical Scientists in the annotation of genetic variants associated with Parkinson’s disease. The system allows users to upload, process and query variant data through a web-based interface.

The application integrates external variant resources (e.g. VariantValidator and ClinVar) to retrieve clinically relevant variant information. It is implemented as a Flask web application, with SQLAlchemy used for database management, and bioinformatic tools and resources for data extraction (e.g. NCBI Entrez), supported by custom utility modules (e.g. clinvar_fetch.py, variantvalidator_fetch.py).


## Project Structure

The Parkinson's Annotator project follows a modular structure, and the main directories and files are organised as follows:

```
parkinson-annotator/
├── docs/   
│   ├── DOCKER.md
│   ├── INSTALLATION.md
│   ├── TECHNICAL_MANUAL.md
│   ├── USER_MANUAL.md
│   └── index.md
├── src/
│   ├── logs/
│   │   └── parkinsons_annotator.log             
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
│       │   ├── data_checks.py
│       │   └── variantvalidator_fetch.py
│       ├── logger.py
│       └── main.py
├── tests/
├── uploads/
├── Dockerfile                        
├── Jenkinsfile                       
├── README.md  
├── environment.yml                   
├── jenkins_pipeline_console_log.txt  
├── mkdocs.yml                        
├── pyproject.toml                    
└── running_main.pdf                  
```



| Directory/File                      | Description                                                  |
|-------------------------------------|--------------------------------------------------------------|
| `docs/`                             | Project documentation (e.g. installation, user, technical, Docker)  |
| `src/logs/`                         | Log directory created automatically by the logging system (not tracked by Git) |
| `parkinsons_annotator.log`          | Rotating log file (not tracked by Git)                       |
| `src/parkinsons_annotator/`         | Main application source code                                 |
| `modules/`                          | Core application logic (e.g. database, routes, data extraction)     |
| `templates/`                        | HTML templates used by the Flask web interface               |
| `utils/`                            | Helper functions for external API access and validation      |
| `logger.py`                         | Logging configuration                                        |
| `main.py`                           | Application entry point                                      |
| `tests/`                            | Automated unit tests                                         |
| `uploads/`                          | Directory for user-uploaded files                            |
| `Dockerfile`                        | Docker build instructions                                    |
| `Jenkinsfile`                       | Defines Jenkins CI pipeline                                  |
| `environment.yml`                   | Conda environment specification                              |
| `jenkins_pipeline_console_log.txt`  | Saved Jenkins build output                                   |
| `mkdocs.yml`                        | MkDocs site configuration                                    |
| `pyproject.toml`                    | Python project dependencies                                  |
| `running_main.pdf `                 | ?needed                                                      |


## Installation

The instructions for setting up the development environment, installing dependencies, and configuring the project can be found in [INSTALLATION.md](./INSTALLATION.md).


## Configuration (move to Installation.md?)

After installing Parkinson's Annotator, the application must be configured using environment variables defined in a `.env` file located in the project root. This approach allows sensitive or environment-specific values to be managed separately from the source code.

To initialise the configuration, copy the provided `.env.example` file and rename it to `.env`:
```sh
cp .env.example .env
```

Next, update the `.env` file with the key configuration options outlined below:

| Variable         | Description                                         | Default                   |
|------------------|-----------------------------------------------------|---------------------------|
| `DB_NAME`        | Name of the SQLite database file                    | parkinsons_data.db        |
| `ENTREZ_EMAIL`   | Email address for NCBI Entrez API access (required) | your@email.com            |


> **Note:**
>
> - The `ENTREZ_EMAIL` variable is required by NCBI to identify users of the Entrez API.
> - Any changes to database configuration or API credentials should be applied to the `.env` file before running the application.


## Running the Application (move to USER_MANUAL.md?)

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

For instructions on how to use the application, see [USER_MANUAL.md](./USER_MANUAL.md).


## Logging

The Parkinson's Annotator application includes a logging system to support debugging and error reporting during development and execution. Logging is configured in the `logger.py` file, and the standard Python logging levels are used (e.g. `DEBUG`, `INFO`, `WARNING`, `ERROR`).

The application writes log messages to 2 destinations:

1. **Console output:**
    
    - Displays log messages during runtime  
    - Configured at the `DEBUG` level for detailed information

2. **Log file:**
    - Stored in the `logs/` directory
    - File name: `parkinsons_annotator.log`
    - Configured at the `WARNING` level, with the following behaviour:
        - Maximum log file size: **500 KB**
        - Number of backup files retained: **2**
        - When the maximum size is reached, older logs are rotated automatically, to ensure logging does not consume excessive disk space.

Logging behaviour can be adjusted by editing the configuration in `logger.py`.


## Testing

Automated tests use the `pytest` framework, and are located in the `tests/` directory.

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
New tests can be added to the `tests/` directory.


## Continuous Integration (CI)

Automated build abd testing verification is managed via [Jenkins](https://www.jenkins.io/).  
The continuous integration (CI) workflow is defined within the `Jenkinsfile`, which includes the following stages:

- Retrieving the source code from the repository
- Setting up the Conda environment
- Installing required project dependencies
- Executing the automated test suite with coverage reporting

Any changes to the CI workflow should be implemented within the `Jenkinsfile`, and validated before merging.


## Documentation

Project documentation is generated using [MkDocs](https://www.mkdocs.org/) to build user-friendly documentation.













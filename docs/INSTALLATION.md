# Installing Parkinson's Annotator

## Introduction

This installation guide walks through how to install the Parkinson's Annotator app on your local machine. 
This guide covers source installation only, for installation and running in Docker please see the [Docker manual](DOCKER.md).

## Installation types

The application can be installed and run from source on Linux and macOS systems. Windows users can run the app in a 
Docker container as described in the [Docker manual](DOCKER.md).

## System requirements

Ensure the following are installed on your system:
- Python 3.13 or later
- pip (Python package manager)
- Git (for cloning the repository)

Recommended:
- Conda (for environment management)

## Before you begin

The application requires a number of Python packages, which are installed using `pip`. This guide recommends using a 
virtual environment to isolate the packages from your system Python installation.  

An `environment.yml` file is provided for Conda to create a virtual environment with the required Python version.

## Installation steps

The following procedure explains how to install the application **Parkinson's Annotator**.

Get started by cloning the repository:

### Step 1 - Clone the GitHub repository

Clone the GitHub repository and move into the project directory:

```bash
git clone https://github.com/JellyEllie/parkinson-annotator.git
cd parkinson-annotator
```

### Step 2 - (Recommended) Create a virtual environment

If using Conda, create a virtual environment using the provided `environment.yml` file:  
```bash
conda env create -f environment.yml
```

Then activate the conda environment:  
```bash
conda activate parkinsons-env
```

### Step 3 - Install dependencies
Install the application and its dependencies via pip:  
```bash
pip install .
```
This installs all runtime dependencies defined in the `pyroject.toml` file. For development, install the 
development dependencies (pytest and pytest-cov) with:  
```bash
pip install .[dev]
```


### Step 4 - Configure environment variables
For NCBI Entrez API access, an access email is required. Provide your email address as an environment variable in the
`.env.example`:  
#### 4.1 Substep 1 - Find the `.env.example` file
Locate the `.env.example` file in the project root directory
#### 4.2 Substep 2 - Rename the `.env.example` file
Rename the `.env.example` to `.env` so it is visible to the application:  
`cp .env.example .env`
#### 4.3 Substep 3 - Add your email address to the `.env` file
Enter your own email address under the `ENTREZ_EMAIL=` variable:  
`ENTREZ_EMAIL= caitlin@example.com`

### Step 5 - Run the application
Run the application by entering the following in your terminal while in the project root directory:  
```bash
parkinsons_annotator
```
This will:

- Create the database if it does not yet exist 
- Create all required tables
- Start the Flask web server

The application will open in your default browser at `http://127.0.0.1:5000`. (This behaviour applies to the source 
installation only. When running in Docker the user must navigate to the browser and navigate to the address manually.)

## Stopping the application

The application can be stopped by pressing `Ctrl+C` in the terminal. Ensure to also close the application webpage.

## Post installation

### Uninstallation 
If the package was installed within a conda environment, first ensure that the environment is active:  
```bash
conda activate parkinsons-env
```  

Uninstall the package:
```bash
pip uninstall parkinsons-annotator
````

And delete the conda environment:
```bash
conda deactivate
conda env remove -n parkinsons-env
```

## Troubleshooting
### Application fails to start
**Solution**:
- Ensure the virtual environment is activated
- Confirm Python version is 3.13 or later
- Check logs in /src/logs/parkinsons_annotator.log

### Database errors
**Solution**
- Verify /src/instance/ exists and contains `parkinsons_data.db`
- Check files have been uploaded to /src/uploads/
   
   
   

*This manual was written using the Installation Manual template provided by [The Good Docs Project](https://www.thegooddocsproject.dev/)*

# parkinson-annotator

## Project description and aims

### Case Summary: 

### Aims:

### Milestones:
1. Extract data from various input files
2. load data in SQL 
3. Incroporate clinvar API 
4. create a search function for querying data 


## Installation and Usage 
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

## Pipeline Architecture

## Project File Structure 

## Data

## Pipeline Build

## License
Probably MIT
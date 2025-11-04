#!/usr/bin/env python3

class  DataExtractor: 

"""
A class for extracting Parkinson's patient data from various file types. 

Methods
-------

extract_zip(zip_path, extract_to)
        Extracts ZIP files to a directory.

read_csv(file_path)
        Reads a CSV file into a DataFrame.

read_vcf(file_path)
        Reads a VCF file into a DataFrame.
"""

	def __init__(self, data_dir="data"):
        """
        Initialises the extractor with a directory to store extracted files.
        """
	

	def extract_zip:


	def read_csv(self, file_path): 
	
        """Reads a CSV file into a pandas DataFrame."""
        return pd.read_csv(file_path)

	
	def read_vcf(self, file_path):
        """Reads a VCF file into a pandas DataFrame."""
        rows = []
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith("#"):
                    continue
                rows.append(line.strip().split("\t"))
        df = pd.DataFrame(rows)
        return df

	def df_to_sqlite(args):
	

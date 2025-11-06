import os
import json
from dotenv import load_dotenv
import modules.database_creation as dc
import modules.database_extractor as de
import utils.clinvar_fetch as cf
import utils.variantvalidator_fetch as vv
from logger import logger

load_dotenv()  # Load environment variables from .env file

DB_NAME = os.getenv("DB_NAME", "parkinsons_data.db")

logger.info("Starting Parkinsons Annotator Application")

dc.create_table_schemas(DB_NAME) # Ensure the database and table are created
de.load_and_insert_data() # Load data and insert into the database

hgvs_variant = "NM_001377265.1:c.841G>T"
clinvar_output= cf.fetch_clinvar_record(hgvs_variant)
print(json.dumps(clinvar_output, indent=4))

variant_description = "17:45983420:G:T"
variant_validator_output = vv.fetch_variant_validator(variant_description)
print(json.dumps(variant_validator_output, indent=4))
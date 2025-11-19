import os
from pathlib import Path
import threading
import webbrowser
from dotenv import load_dotenv
from flask import Flask

from .logger import logger
from .modules.db import close_db_session, has_full_data, create_db_engine, create_tables
from .modules.database_creation import create_db_and_tables
from .modules.data_extraction import load_and_insert_data
from .modules.routes import route_blueprint
# from .modules import create_db_and_tables, load_and_insert_data, route_blueprint

load_dotenv()  # Load environment variables from .env file

DB_NAME = os.getenv("DB_NAME", "parkinsons_data.db")

# Opens the URL when program is run
def open_browser():
    '''The specified URL (whiich is the default created by the command to create the interface)'''
    webbrowser.open_new("http://127.0.0.1:5000/")

def main():
    logger.info("Starting Parkinsons Annotator Application")

    # Set template_folder to the templates directory within the modules folder, so Flask can find the HTML files
    app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))
    app.config['DB_NAME'] = DB_NAME
    app.teardown_appcontext(close_db_session)  # Ensure DB session is closed after each request
    app.register_blueprint(route_blueprint)

    with app.app_context():
        # Also need to check if the database is fully populated
        if not Path(DB_NAME).exists():
            logger.info(f"Database '{DB_NAME}' not found. Creating new database and loading data.")
            # create_db_and_tables(DB_NAME) # Ensure the database and table are created
            create_db_engine()          # Create the database engine
            create_tables()             # Create tables in the database

        # if not has_full_data():
            load_and_insert_data() # Load data and insert into the database
            # enrich_database()

    # Do the API bits to grab the extra data here before starting the app
    # if not has_full_data(DB_NAME):
    #     enrich_database(DB_NAME)
    # app.run(host='
    threading.Timer(1, open_browser).start()    # Opens the interface, several things happen at once for this to work
    app.run(debug=True, use_reloader=False)     # Prevents two interfaces from opening

if __name__ == "__main__":
    main()

# poetry -> main -> {
#     if not then create_db
#     make sure data is full
#     start app
#     re-run db insert for uploads after new upload
# }





# import os
# import json
# from dotenv import load_dotenv
# import modules.database_creation as dc
# import modules.database_extractor as de
# import utils.clinvar_fetch as cf
# import utils.variantvalidator_fetch as vv
# from logger import logger

# load_dotenv()  # Load environment variables from .env file

# DB_NAME = os.getenv("DB_NAME", "parkinsons_data.db")

# logger.info("Starting Parkinsons Annotator Application")

# dc.create_table_schemas(DB_NAME) # Ensure the database and table are created
# de.load_and_insert_data() # Load data and insert into the database

# hgvs_variant = "NM_001377265.1:c.841G>T"
# clinvar_output= cf.fetch_clinvar_record(hgvs_variant)
# print(json.dumps(clinvar_output, indent=4))

# variant_description = "17:45983420:G:T"
# variant_validator_output = vv.fetch_variant_validator(variant_description)
# print(json.dumps(variant_validator_output, indent=4))
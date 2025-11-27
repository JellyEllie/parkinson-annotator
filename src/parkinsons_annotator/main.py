import os
from pathlib import Path
import threading
import webbrowser
from dotenv import load_dotenv
from flask import Flask

from parkinsons_annotator.logger import logger
from parkinsons_annotator.modules.db import close_db_session, create_db_engine, create_tables, has_full_data
from parkinsons_annotator.modules.routes import route_blueprint
from parkinsons_annotator.modules.data_extraction import load_and_insert_data

load_dotenv()  # Load environment variables from .env file

DB_NAME = os.getenv("DB_NAME", "parkinsons_data.db")


# Opens the URL when program is run
def open_browser():
    """The specified URL (whiich is the default created by the command to create the interface)"""
    webbrowser.open_new("http://127.0.0.1:5000/")

def main():
    logger.info("Starting Parkinsons Annotator Application")

    # Set template_folder to the templates directory within the modules folder, so Flask can find the HTML files
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "templates"),
        instance_relative_config=True
    )

    # Create instance folder if needed
    Path(app.instance_path).mkdir(exist_ok=True)

    # Set upload folder to within Flask instance folder
    upload_path = Path(app.instance_path) / "uploads"
    upload_path.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = str(upload_path)

    # Put database within instance folder too because it is written at runtime
    db_path = Path(app.instance_path) / DB_NAME
    app.config["DB_NAME"] = str(db_path)

    # Ensure DB session is closed after each request
    app.teardown_appcontext(close_db_session)

    # Register the blueprint
    app.register_blueprint(route_blueprint)

    with app.app_context():
        # If database does not exist, create database and tables
        if not db_path.exists():
            logger.info(f"Database '{DB_NAME}' not found. Creating new database and tables.")
            create_db_engine()          # Create the database engine and session
            create_tables()             # Create tables in the database

        # Load initial data if a table is empty
        if not has_full_data():
            try:
                logger.info("Loading initial data into the database...")
                load_and_insert_data()
            except Exception as e:
                logger.error(f"Failed to load initial data: {e}")

    # Do the API bits to grab the extra data here before starting the app
    # if not has_full_data(DB_NAME):
    #     enrich_database(DB_NAME)
    # app.run(host='

    # Open browser after 1 second
    threading.Timer(1, open_browser).start()

    # Start the Flask app
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
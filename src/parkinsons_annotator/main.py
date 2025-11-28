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

def create_app():
    logger.info("Building app")

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

    return app

def main():
    logger.info("Starting Parkinsons Annotator Application")

    app = create_app()

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

    # Open browser after 1 second
    threading.Timer(1, open_browser).start()

    # Start the Flask app
    app.run(debug=True, use_reloader=False)     # Prevents two interfaces from opening

if __name__ == "__main__":
    main()
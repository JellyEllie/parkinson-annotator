import os
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv

from .logger import logger
from .modules.routes import route_blueprint
from .modules.db import close_db_session, create_db_engine, create_tables
from .modules.data_extraction import load_and_insert_data

def create_app(test_config=None):
    """
    Flask application factory for the Parkinsons Annotator.
    This function handles:
      - loading environment variables
      - setting up Flask + config
      - initializing database + tables
      - ensuring initial data is loaded
      - registering routes/blueprints
      - setting teardown behavior
      """

    # Load variables from .env file
    load_dotenv()

    # Set up Flask app
    app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))

    # Get database name from .env (with default fallback)
    db_name = os.getenv("DB_NAME", "parkinsons_data.db")
    app.config["DB_NAME"] = db_name

    # Ensure DB session is closed after each request
    app.teardown_appcontext(close_db_session)

    # Register blueprint
    app.register_blueprint(route_blueprint)

    # Database setup
    with app.app_context():
        db_path = Path(app.config["DB_NAME"])
        # TODO: Add check for database being fully populated
        if not db_path.exists():
            logger.info(f"Database {db_path} not found — creating new database and loading data.")
            create_db_engine()  # Create the database engine to connect to database
            create_tables()     # Create tables in the database
            load_and_insert_data()  # Load data and insert into the database

    # Log app creation
    logger.info("Flask application created successfully.")

    return app




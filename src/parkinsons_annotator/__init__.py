import os

from flask import Flask
from dotenv import load_dotenv


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

    # set up Flask app
    app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))

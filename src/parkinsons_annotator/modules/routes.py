"""
This script creates the user interface and generates vriables from the search and input sections which can be used within the rest of the program
The visuals and interactive elements of the interface are stored in a html file
"""

import os
import signal
from flask import Blueprint, render_template, request, jsonify, current_app as app
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from .database_search import database_list, SearchFieldEmptyError, NoMatchingRecordsError
from .data_extraction import load_and_insert_data
from src.parkinsons_annotator.logger import logger

route_blueprint = Blueprint('routes', __name__)

@route_blueprint.route('/', methods=['GET'])
def index():
    """This function opens the html file which contains the interface informtion"""
    # return render_template("interface_package.html")
    return render_template("interface_package.html")

@route_blueprint.route('/shutdown', methods=['POST'])
def shutdown_server():
    """This function shuts the server, which will be activated from inside the html file, triggered by the web browser shutting down"""
    func = request.environ.get('werkzeug.server.shutdown')  # Calls from a WSGI enviornment using a speical key which shuts down the Flask server
    if func:
        func()                                              # If the shut down function isn't found, don't shut down the server
    else:
        os.kill(os.getpid(), signal.SIGINT)                 # Sends an interupt signal (kill) to the current process ID (getpid). This is the equivalant of typing in Ctl + C

@route_blueprint.route('/search', methods=['POST'])
def search():
    """Handle search queries from the interface."""
    data = request.get_json()
    search_value = data.get('query', '').lower().strip()
    search_type = data.get('category', '').lower().strip()

    logger.info(f"User searched for: {search_value}, category: {search_type}")

    # Call the database search function
    try:
        results = database_list(search_type=search_type, search_value=search_value)
    except SearchFieldEmptyError:
        return jsonify({"message": "Missing search fields"}), 400
    except NoMatchingRecordsError:
        return jsonify({"message": "No matching records found"}), 404
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        return jsonify({"message": "Internal server error"}), 500

    return jsonify({"results": results}), 200

@route_blueprint.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return "No file part in the request", 400

    file = request.files['file']  # Get file from form

    if file.filename == '':
        return "No file selected", 400

    # Save the file
    # filepath = os.path.join(app.config['upload_folder'], file.filename)

    # UPLOAD_FOLDER = 'uploads'  # folder name
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # create it if it doesn’t exist
    app.config['upload_folder'] = UPLOAD_FOLDER

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # TODO: This route handler doesn't handle errors during data insertion
    # So causes upload failed alert to the user and a flask crash if something goes wrong
    load_and_insert_data()

    logger.info( file.filename )
    return f"File '{file.filename}' uploaded and stored successfully!"

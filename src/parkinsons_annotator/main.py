"""
main.py
Launch script for the Parkinson's Annotator Flask application.

This script:
    - Starts the Flask development server
    - Automatically opens the user's browser to the app homepage
"""

import threading
import webbrowser
from parkinsons_annotator.logger import logger
from parkinsons_annotator import create_app


def open_browser():
    """Wait briefly, then open the default browser to the Flask app URL."""
    webbrowser.open_new("http://127.0.0.1:5000")


def run_app():
    """Create the Flask app and run the development server."""
    app = create_app()
    app.run(debug=True, use_reloader=False)  # Prevents two interfaces from opening


if __name__ == "__main__":
    # Open browser in separate thread so it doesn't block Flask
    threading.Timer(1, open_browser).start()  # Opens the interface, several things happen at once for this to work
    # Run Flask directly
    run_app()

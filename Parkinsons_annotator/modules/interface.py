'''
This script creates the user interface and generates vriables from the search and input sections which can be used within the rest of the program
The visuals and interactive elements of the interface are stored in a html file
'''

# Flask is to module which is used to create the interface. render_template allows for more complex design,
# request allows for pulling data input into the interfce, jsonify outputs the data into the interface 
from flask import Flask, render_template, request, jsonify

# Allows the interface to be opened in web browser from the script being run
import webbrowser

# Allows the script tonrun multiple porcesses at once
import threading

# Is a standard labray module that allows interaction with the program e.g. checking if files or directories exist
import os

# Handles interactions from the interface, will be used to close Flask when program is not in use
import signal

# Creates the Flask server
app = Flask(__name__)

# Creates the url/opens the interface web browser
@app.route("/")

# Opens the interface data
def index():
    '''This function opens the html file which contains the interface informtion'''
    return render_template("interface_package.html")

# Creates the route to shut down the Flask server when directed
@app.route('/shutdown', methods=['POST'])

# Function to shut down the Flask server
def shutdown_server():
    '''This function shuts the server, which will be activated from inside the html file, triggered by the web browser shutting down'''
    func = request.environ.get('werkzeug.server.shutdown')  # Calls from a WSGI enviornment using a speical key which shuts down the Flask server
    if func:
        func()                                              # If the shut down function isn't found, don't shut down the server
    else:
        os.kill(os.getpid(), signal.SIGINT)                 # Sends an interupt signal (kill) to the current process ID (getpid). This is the equivalant of typing in Ctl + C

# Opens the URL when program is run
def open_browser():
    '''The specified URL (whiich is the default created by the command to create the interface)'''
    webbrowser.open_new("http://127.0.0.1:5000/")

# Creates the route to be able to pull the info from the search bar in the interface
@app.route('/search', methods=['POST'])

# Function to work with the search query to get the input from the search bar
def search():
    '''This function pulls the query from the database, converts it to lowercase, peints the search to the command line, and returns it to the interface'''
    
    # Pull the json data from the search. Query is defined in the html file, tring converted to lowercase, makes for a cae insensetive search
    query = request.json.get('query', '').lower()  # Empty string returned if nothing entered
    
   # Print used to check the input works as it currently doesn't have any results to return
    print("User searched for:", query)

    # Return a response to the interface. This is also currently unecessary. To remove later
    return jsonify(query)

# Function to store the uploaded file
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return "No file part in the request", 400

    file = request.files['file']  # Get file from form

    if file.filename == '':
        return "No file selected", 400

    # Save the file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    return f"File '{file.filename}' uploaded and stored successfully!"
    print( file.filename )

# Runs the functions that are needed to start everything
if __name__ == "__main__":
    threading.Timer(1, open_browser).start()    # Opens the interface, several things happen at once for this to work
    app.run(debug=True, use_reloader=False)     # Prevents two interfaces from opening


  # decorator to route URL 
#@app.route('/help') 

# binding to the function of route 
#def hello_world():     
 #   return 'hello world'
  
  

#if __name__=='__main__': 
 #  app.run(debug=True)
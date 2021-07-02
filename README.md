# LegalMation Backend Coding Challenge
### Austin Byron

## In order to run for the first time
1. Create a virtual environment with Python 3.9.5 in the directory where this project is located.
2. Activate the virtual environment from the command line.
3. From inside the folder that this project is located, run the command 'pip install -r requirements.txt' from the command line (you will need to have pip installed to be able to do this, see: https://pip.pypa.io/en/stable/installing/ if you need to install pip).
4. From inside the folder that this project is located, run the command 'python SQLSetup.py' from the command line, which creates a file called database.db.
5. From inside the folder that this project is located, run the command 'python App.py' from the command line, which starts up the web interface for the project.
6. Go to http://127.0.0.1:5000/ from your web browser and begin using the project.

## In order to run any time after the first time
1. Go to the directory where this project is located and activate the virtual environment
2. From inside the project directory, run the command 'python App.py' from the command line **make sure you already ran the command 'python SQLSetup.py' once when you first set up the project before you do this step**
3. Go to http://127.0.0.1:5000/ from your web browser and begin using the project.


## Curl Commands
*See the documentation.md file for more information on these curl commands*  
- Add a file to the database -> 'curl -X POST -F 'file=@<path/to/file.xml>' -F 'json=on' http://127.0.0.1:5000/process'
    - Returns the parsed plaintiff(s) and defendant(s) from the file and adds them to the database
- View the database as JSON -> 'curl http://127.0.0.1:5000/records.json'
    - Returns the database as a JSON file
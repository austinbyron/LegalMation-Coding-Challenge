import os
from flask import Flask, redirect, render_template, url_for, request, session
import sqlite3
import json
from datetime import datetime
from ParseInputs import process_content


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = ['.xml']


app = Flask(__name__)
app.config['UPLOAD_PATH'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ALLOWED_EXTENSIONS
app.secret_key = "shhhh dont tell anyone the s3cr3t key"


@app.route('/')
def upload_file():
    return render_template('upload.html')


@app.route('/process', methods=['POST'])
def process_file():
    if request.method == 'POST':
        f = request.files['file']

        # If there was a file submitted
        if f.filename != '':

            # Double check that the file is an xml file
            file_extension = os.path.splitext(f.filename)[1]
            if file_extension not in app.config['UPLOAD_EXTENSIONS']:
                os.abort(400)

            # Save the file to be processed
            f.save(os.path.join(app.config['UPLOAD_PATH'], f.filename))
            
            # Process and parse the file for the plaintiff(s) and defendant(s)
            plaintiff, defendant = process_content(os.path.join(app.config['UPLOAD_PATH'], f.filename))
            session['plaintiff'] = plaintiff
            session['defendant'] = defendant
            
            # Remove the file once we are done using it
            os.unlink(os.path.join(app.config['UPLOAD_PATH'], f.filename))


        # If no file was submitted, enter manual mode and make sure to set
        # the session values for plaintiff and defendant to empty strings
        else:
            session['plaintiff'] = ""
            session['defendant'] = ""

        # If user requests the data in JSON form
        if request.form.get('json'):
            
            # Try to add the current session to the database, and if you succeed,
            # then return the plaintiff and defendant as results in JSON
            succeeded = add_session_to_database(from_json=True)

            # Follow JSONAPI format for JSON response
            json_api = {
                "links": {
                    "self": "http://127.0.0.1:5000/process",
                }
            }
            if succeeded:
                json_api['links']['related'] = "http://127.0.0.1:5000/records.json"
                json_api['data'] = [
                    {
                        "type": "plaintiff",
                        "attributes": {
                            "extracted_name": session["plaintiff"]
                        }
                    },
                    {
                        "type": "defendant",
                        "attributes": {
                            "extracted_name": session["defendant"]
                        }
                    }
                ]
                return json.dumps(json_api)
            else:
                json_api['errors'] = {
                    "status": 400,
                    "title": "An unknown error has occurred"
                }
                return json.dumps({"message": "error"})

        # Otherwise, when processed, go to validation page
        else:
            return redirect(url_for('validate'))


    
@app.route('/validate')
def validate():

    # Get the plaintiff and defendant from the current session, and render
    # validate.html for user confirmation and final user clean up if they would
    # like to change anything about the parsed data

    p = session['plaintiff']
    d = session['defendant']
    
    return render_template('validate.html', plaintiff=p, defendant=d)


@app.route('/confirmation', methods=['POST'])
def confirmation():
    
    # Try to add the current session to the database, and if you succeed,
    # then redirect to view all records in database 

    succeeded = add_session_to_database(from_json=False)

    if succeeded:
        return redirect(url_for('view_records'))
    else:
        # Follow JSONAPI format for error response
        json_api = {
            "links": {
                "self": "http://127.0.0.1:5000/confirmation"
            },
            "errors": {
                "status": 400,
                "title": "An unknown error has occurred"
            }
        }
        return json.dumps(json_api)



@app.route('/records')
def view_records():

    # Establish connection to the database, then fetch all rows from extractions
    # and pass the rows to the viewdb.html page and render viewdb.html

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    curs = conn.cursor()
    curs.execute("select * from extractions")  
    records = curs.fetchall()

    return render_template("viewdb.html", records=records)

@app.route('/records.json')
def view_records_json():

    # Follow JSONAPI format for JSON response
    json_api = {
        "links": {
            "self": "http://127.0.0.1:5000/records.json"
        },
    }

    try:
        # Establish connection to the database, then fetch all rows from extractions
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        curs = conn.cursor()
        curs.execute("select * from extractions")  
        records = curs.fetchall()

        # Turn each row into a list, and add format the list into a map showing
        # docid, plaintiff, defendant, and timestamp, and return that data
        data = []
        for r in records:
            lr = list(r)
            entry = {
                "type": "record",
                "attributes": {
                    "docid": lr[0],
                    "plaintiff": lr[1],
                    "defendant": lr[2],
                    "timestamp": lr[3]
                }
            }
            data.append(entry)
        conn.close()
        json_api['data'] = data
        return json.dumps(json_api)
    except:
        json_api['errors'] = {
            "status": 400,
            "title": "An unknown error has occurred"
        }
        return json.dumps(json_api)

def add_session_to_database(from_json):
    
    succeeded = False
    try:
        # Connect to the sqlite database
        conn = sqlite3.connect('database.db')
        curs = conn.cursor()

        # Count the number of rows for a naive document id
        curs.execute("select * from extractions")
        results = curs.fetchall()
        document_num = len(results)

        # If the user requested the response as json, pull directly from session
        if from_json:
            plaintiff = session["plaintiff"]
            defendant = session["defendant"]
        else:
            # Get the plaintiff and defendant from the input form from validate.html
            plaintiff = request.form['plaintiff']
            defendant = request.form['defendant']

        # Get iso timestamp for the time entered into the database
        date = datetime.now().isoformat()
            
        # Input and commit the data into the extractions database
        curs.execute("INSERT INTO extractions (docid, plaintiff, defendant, date) VALUES (?,?,?,?)", (document_num, plaintiff, defendant, date))
        conn.commit()
        
        succeeded = True

    except:
        # If there was an error, rollback to previous commit and return Error
        conn.rollback()
        succeeded = False
        

    finally:
        # Close the connection and return whether it succeeded
        conn.close()
        return succeeded

if __name__ == '__main__':
    app.run(debug=False, port=5000)
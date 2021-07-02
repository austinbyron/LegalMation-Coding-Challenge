There are two endpoints that return JSON documents that conform to the JSON API spec.

You can use curl commands to access these endpoints:

### 'curl -X POST -F 'file=@<path/to/file.xml>' -F 'json=on' http://127.0.0.1:5000/process'

- This command uploads xml file you choose, parses the document for the plaintiff(s) and defendant(s), and then adds those plaintiff(s) and defendant(s) to the database.

Example:  
```
{
    "links": {
        "self": "http://127.0.0.1:5000/process", 
        "related": "http://127.0.0.1:5000/records.json"
    }, 
    "data": [
        {
            "type": "plaintiff", 
            "attributes": {
                "extracted_name": "Mr. Plaintiff"
            }
        }, 
        {
            "type": "defendant", 
            "attributes": {
                "extracted_name": "Mr. Defendant"
            }
        }
    ]
}
```

### 'curl http://127.0.0.1:5000/records.json'

- This command pulls all of the rows/records from the database and returns them in JSON format to allow users to view previous documents that have been entered in hte database.
    - Each row contains a document ID, the plaintiffs' names, the defendants' names, and the timestamp for when that particular row was added to the database.

Example:  
```
{
    "links": {
        "self": "http://127.0.0.1:5000/records.json"
    }, 
    "data": [
        {
            "type": "record", 
            "attributes": {
                "docid": "0",
                "plaintiff": "First plaintiff name", 
                "defendant": "First defendant name", 
                "timestamp": "2021-06-26T01:02:33.043687"
            }
        }, 
        {
            "type": "record", 
            "attributes": {
                "docid": "1",
                "plaintiff": "Second plaintiff name", 
                "defendant": "Second defendant name", 
                "timestamp": "2021-06-26T01:03:18.281708"
            }
        }, 
        {
            "type": "record", 
            "attributes": {
                "docid": "2", 
                "plaintiff": "Third plaintiff name", 
                "defendant": "Third defendant name", 
                "timestamp": "2021-06-26T01:09:58.026745"
            }
        }, 
        {
            "type": "record", 
            "attributes": {
                "docid": "3", 
                "plaintiff": "Fourth plaintiff name", 
                "defendant": "Fourth defendant name", 
                "timestamp": "2021-06-26T01:10:07.369491"
            }
        }
    ]
}
```
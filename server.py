from flask import Flask, jsonify, request
import sqlite3


app = Flask(__name__) #create a flask instance


DB_NAME = "budget_manager.db" 

def init_db():
    connection = sqlite3.connect(DB_NAME) # open a connection to the D.B named "budget_manager.db"
    cursor = connection.cursor() # creates a cursor/tool that lets you send commands (INSERT, SELECT, etc.) to the database

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    connection.commit() # save changes to the D.B.
    connection.close() # close the connection to the D.B.

#http://localhost:5000/api/health 
@app.get("/api/health") 
def health_check():
    return jsonify({
        "status": "OK"
    }), 200 #now we can use just the number for the status


# ---- USERS -----
#http://127.0.0.1:5000/api/users
@app.post("/api/users")
def register():
    new_user = request.get_json() 
    print(new_user)
    
    username = new_user["username"] 
    password = new_user["password"]
    
    connection = sqlite3.connect(DB_NAME) # open the connection to the D.B. (open the book)
    cursor = connection.cursor() # create a cursor/tool to send commands to the D.B.  (pencil to write in the book)
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password)) # executes sql statement (write in the book)
    connection.commit() # save changes to the D.B. (close the book)
    connection.close() # close the connection to the D.B. (put away the book)

    return jsonify({
        "success": True,
        "message": "user created successfully"
    }), 201 #created

# GET http://127.0.0.1:5000/api/users
@app.get("/api/users")
def get_users():
    connection = sqlite3.connect(DB_NAME) # open the connection to the D.B. (open the book)
    connection.row_factory = sqlite3.Row # allows columns values to be retrieve by name, row["username"] 
    cursor = connection.cursor() # create a cursor/tool to send commands to the D.B.
    cursor.execute("SELECT * FROM users") 
    rows = cursor.fetchall() # fetch all the results from the query (read the book)
    print(rows)
    connection.close() 
    
    users = []
    for row in rows:
        print(dict(row))
        users.append(dict(row)) 

    return jsonify({
        "success": True,
        "message": "users retrieved successfully",
        "data": users
    })

if __name__ == "__main__":
    init_db() 
    app.run(debug=True) #run the flask app in debug mode

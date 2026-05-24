from flask import Flask, jsonify, request
import sqlite3
from datetime import date


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
    
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT NOT NULL,
            amount INTEGER NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
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


# GET http://127.0.0.1:5000/api/users/2
@app.get("/api/users/<int:user_id>")
def get_user_by_id(user_id):
    connection = sqlite3.connect(DB_NAME) 
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        return jsonify({
            "success": False,
            "message": "user not found"
        }), 404 

    print(f"row: {row}") 
    user_information = dict(row) 
    connection.close()

    return jsonify({
        "success": True,
        "message": "user retrieved successfully",
        "data": user_information
    }), 200


# PUT http://127.0.0.1:5000/api/users/2
@app.put("/api/users/<int:user_id>")
def update_user_by_id(user_id):
    updated_user = request.get_json()
    
    username = updated_user["username"]
    password = updated_user["password"]
    
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    
    #validation 
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        return jsonify({
            "success": False,
            "message": "user not found"
        }), 404
    
    cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (username, password, user_id))
    connection.commit()
    connection.close()
    
        
    return jsonify({
        "success": True,
        "message": "user updated successfully"
    }), 200




#DELETE http://127.0.0.1:5000/api/users/2

@app.delete("/api/users/<int:user_id>")
def delete_user_by_id(user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        return jsonify({
            "success": False,
            "message": "user not found"
        }), 404


    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    connection.commit()
    connection.close()
    
    return jsonify({
        "success": True,
        "message": "user deleted successfully"
    }), 200


# ---- EXPENSES -----
# POST http://127.0.0.1:5000/api/expenses

@app.post("/api/expenses")
def create_expense():
    new_expense = request.get_json()
    print(new_expense)
    
    title = new_expense.get("title", "")
    description = new_expense.get("description", "")
    amount = new_expense.get("amount", 1)
    date_expense = new_expense.get("date", date.today()) 
    category = new_expense.get("category", "")
    user_id = new_expense.get("user_id", 2)
    
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute(""" 
        INSERT INTO expenses (title, description, amount, date, category, user_id)
        VALUES (?, ?, ?, ?, ?, ?)""", (title, description, amount, date_expense, category, user_id))
    
    connection.commit()
    connection.close()
    
    return jsonify({
        "success": True,
        "message": "expense created successfully"
    }), 201


# GET http://127.0.0.1:5000/api/expenses
@app.get("/api/expenses")
def get_expenses():
    
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    print(f"expenses {rows}")
    
    expenses = []
    for row in rows:
        print(f"row: {dict(row)}")
        expenses.append(dict(row))
    
    return jsonify({
        "success": True,
        "message": "expenses retrieved successfully",
        "data": expenses 
    }), 200


#GET http://127.0.0.1:5000/api/expenses/2
@app.get("/api/expenses/<int:expense_id>")
def get_expense_by_id(expense_id):
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()
    
    if not row:
        return jsonify({
            "success": False,
            "message": "expense not found"
        }), 404
    
    print(f"row: {row}")
    expense_information = dict(row)
    connection.close()
    
    return jsonify({
        "success": True,
        "message": "expense successfully",
        "data": expense_information
    }), 200


# UPDATE http://127.0.0.1:5000/api/expenses/2
@app.put("/api/expenses/<int:expense_id>")
def update_expense_by_id(expense_id):
    updated_expense = request.get_json()
    
    title = updated_expense.get("title", "")
    description = updated_expense.get("description", "")
    amount = updated_expense.get("amount", 1)
    date_expense = updated_expense.get("date", date.today()) 
    category = updated_expense.get("category", "")
    user_id = updated_expense.get("user_id", 2)
    
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    
    #validation 
    cursor.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()
    
    if not row:
        return jsonify({
            "success": False,
            "message": "expense not found"
        }), 404
    
    cursor.execute(""" 
        UPDATE expenses 
        SET title = ?, description = ?, amount = ?, date = ?, category = ?, user_id = ?
        WHERE id = ?""", (title, description, amount, date_expense, category, user_id, expense_id))
    
    connection.commit()
    connection.close()
    
        
    return jsonify({
        "success": True,
        "message": "expense updated successfully"
    }), 200

# DELETE http://127.0.0.1:5000/api/expenses/2
@app.delete("/api/expenses/<int:expense_id>")
def delete_expense_by_id(expense_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()
    
    if not row:
        return jsonify({
            "success": False,
            "message": "expense not found"
        }), 404
    
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    connection.commit()
    connection.close()
    
    return jsonify({
        "success": True,
        "message": "expense deleted successfully"
    }), 200


if __name__ == "__main__":
    init_db() 
    app.run(debug=True) #run the flask app in debug mode

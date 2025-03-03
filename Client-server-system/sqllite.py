import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('mydatabase.db')
cursor = conn.cursor()

# Create a table
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT,
                   password TEXT)''')

# Insert data into the table
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("John Doe", "123456"))
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("Jane Smith", "blue"))
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("John Doe", "blues"))
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("Jane Smith", ""))
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("John jane@example.comDoe", "john@example.com"))
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("John Doe", "john@example.com"))
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("John Doe", "john@example.com"))
# Commit the changes and close the connection
conn.commit()
conn.close()

# Retrieve data from the table
conn = sqlite3.connect('mydatabase.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall() # what to use if there is a response (and save the response and iterate over it)

# Display the retrieved data
for row in rows:
    print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}")

# Close the connection
conn.close()



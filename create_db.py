import sqlite3

# Connect or create a new database
conn = sqlite3.connect("food_calories.db")

# Create a cursor to execute SQL commands
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS food_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    calories REAL NOT NULL,
    protein REAL,
    fat REAL,
    carbs REAL,
    serving_size TEXT
)
''')

# Save and close
conn.commit()
conn.close()

print("✅ Database and table created successfully!")

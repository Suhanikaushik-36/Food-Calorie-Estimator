import sqlite3

conn = sqlite3.connect("food_calories.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM food_data")
for row in cursor.fetchall():
    print(row)

conn.close()

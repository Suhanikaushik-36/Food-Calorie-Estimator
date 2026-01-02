import sqlite3

# Connect to your existing database
conn = sqlite3.connect("food_calories.db")
cursor = conn.cursor()

# Sample food data
foods = [
    ("Apple", 95, 0.5, 0.3, 25, "1 medium"),
    ("Banana", 105, 1.3, 0.4, 27, "1 medium"),
    ("Rice (cooked)", 206, 4.3, 0.4, 45, "1 cup"),
    ("Pasta Alfredo", 420, 14, 22, 45, "1 bowl"),
    ("Pizza Slice", 285, 12, 10, 36, "1 slice"),
    ("Burger", 354, 17, 20, 29, "1 burger"),
    ("Chapati", 120, 3.1, 3.6, 18, "1 piece"),
    ("Paneer Curry", 300, 15, 25, 5, "1 bowl")
]

# Insert data into table
cursor.executemany('''
INSERT INTO food_data (name, calories, protein, fat, carbs, serving_size)
VALUES (?, ?, ?, ?, ?, ?)
''', foods)

conn.commit()
conn.close()

print("✅ Sample food data added successfully!")

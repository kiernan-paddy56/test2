import sqlite3, json #import sql and json for formating
#json allows easy conversion of my map data into database form

connection = sqlite3.connect('maps.db')
cursor = connection.cursor()

def connect_db(db_name='maps.db'):
    return sqlite3.connect(db_name)

cursor.execute('''
CREATE TABLE IF NOT EXISTS maps(
    map_id INTEGER PRIMARY KEY AUTOINCREMENT,
    grid_data TEXT NOT NULL
)
               ''')
connection.commit()
connection.close()

def insert_grid(name, grid):
    conn = connect_db()
    cursor = conn.cursor()




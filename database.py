import sqlite3, json #import sql and json for formating
#json allows easy conversion of my map data into database form


def connect_db(db_name='maps.db'):
    return sqlite3.connect(db_name)

# Function to create the table
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS grids (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        grid_data TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def insert_grid(name, grid):
    conn = connect_db()
    cursor = conn.cursor()
    grid_json = json.dumps(grid)  # Serialize grid (turn to plain string so it can be saved easily)
    cursor.execute('INSERT INTO grids (name, grid_data) VALUES (?, ?)', (name, grid_json))
    conn.commit()
    conn.close()

# Function to fetch a grid by name
def fetch_grid(name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT grid_data FROM grids WHERE name = ?', (name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return json.loads(result[0])  # Deserialize grid
    return None



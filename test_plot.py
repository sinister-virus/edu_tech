current_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the database path
db_path = os.path.join(current_dir, 'edutech_db.accdb')

# Construct the connection string
conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            rf'DBQ={db_path};')

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
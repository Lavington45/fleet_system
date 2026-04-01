import mysql.connector, os

config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'fleet_system'),
}
print('db config', config)

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    print('tables', tables)

    for t in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {t[0]}')
        print(t[0], cursor.fetchone()[0])

    conn.close()
except Exception as e:
    print('DB error', e)

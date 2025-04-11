import pyodbc

conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};'
                      'SERVER=localhost;'
                      'DATABASE=Library;'
                      'UID=sa;'
                      'PWD=123456;'
                      'Encrypt=no')

cursor = conn.cursor()
cursor.execute('SELECT 1')
row = cursor.fetchone()
print(row)

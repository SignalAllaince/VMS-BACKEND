import pyodbc
import bcrypt
def connection():
    conn_str = (
        "DRIVER={MySQL ODBC 8.1 Unicode Driver};"
        "SERVER=vms-server.mysql.database.azure.com;"
        "PORT=3306;"
        "DATABASE=vmsdb;"
        "UID=postman;"
        "PWD=simple@123;"
    )
    return pyodbc.connect(conn_str)

conn = connection()
cursor = conn.cursor()
_username='superadmin'
role='superadmin'
_password='iloverice'
hashed = bcrypt.hashpw(_password.encode("utf-8"), bcrypt.gensalt())
cursor.execute("INSERT INTO admin (username, PasswordHash, role) VALUES (?, ?, ?)", _username, hashed, role)
cunn.commit()
conn.close()
print('successful')

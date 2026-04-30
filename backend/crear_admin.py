from werkzeug.security import generate_password_hash
import mysql.connector
from conexionDB import db_config

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

user = 'admin'
name_user = 'Luis Montes'
password_user = generate_password_hash('123456')
rol_user = 'Admin'

cursor.execute(
    "INSERT INTO users (name_user, password_user, rol_user, user) VALUES (%s, %s, %s, %s)",
    (name_user, password_user, rol_user, user)
)

conn.commit()
cursor.close()
conn.close()

print("Usuario administrador creado")
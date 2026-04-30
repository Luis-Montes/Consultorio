from flask import Flask, render_template, request, session, redirect, url_for, flash
import mysql.connector

from werkzeug.security import generate_password_hash, check_password_hash
from conexionDB import db_config

import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
template_folder = os.path.join(project_root, 'templates')
static_folder = os.path.join(project_root, 'static')

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

app.secret_key = 'clave_secreta_para_sesiones'

# Ruta principal

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    return render_template('plantilla.html')

# Login ====================================
@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None
    if request.method == 'POST':
        user = request.form["user"]
        password = request.form["password_user"]

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE user=%s", (user,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            if check_password_hash(user['password_user'], password):
                session["user"] = {
                    'id_user': user["id_user"],
                    'name_user': user["name_user"],
                    'rol_user': user['rol_user']
                }
                return redirect(url_for('index'))
            else:
                error= 'contraseña incorrecta'
        else:
            error = "Usuario no encontrado"
    
    return render_template('modulos/login.html', error=error)

# LOGOUT ==================================================
@app.route('/logaout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
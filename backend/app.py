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
        
    return redirect(url_for('inicio'))

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
                return redirect(url_for('inicio'))
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

# Mis Datos
@app.route('/mis_datos', methods=["GET", "POST"])
def mis_datos():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    id_user = session['user']['id_user']
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name_user = request.form['name_user']
        user = request.form['user']
        document_user = request.form['document_user']
        phone_user = request.form['phone_user']
        passwordN = request.form['password_user']
        

        cursor.execute("SELECT id_user FROM users WHERE user = %s AND id_user != %s", (user, id_user))

        if  cursor.fetchone():
            flash("El usuario con este nombre ya existe.", "error")
        else:
            if passwordN.strip() != "":
                passwordN = generate_password_hash(request.form['password_user'])
                cursor.execute(""" UPDATE users SET name_user=%s, user=%s, document_user=%s, phone_user=%s, password_user=%s WHERE id_user = %s """,
                               (name_user, user, document_user, phone_user, passwordN, id_user))
                
            else:
                cursor.execute(""" UPDATE users SET name_user=%s, user=%s, document_user=%s, phone_user=%s WHERE id_user = %s """,
                               (name_user, user, document_user, phone_user, id_user))
            conn.commit()
            flash("Datos Actualizados Correctamente", "success")

    cursor.execute("SELECT * FROM users WHERE id_user = %s", (id_user,))

    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('modulos/mis_datos.html', user=user)

# INICIO ============================================
@app.route('/inicio', methods=["GET"])
def inicio():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM inicio WHERE id = 1")
    datosInicio = cursor.fetchone()

    conn.close()

    return render_template('modulos/inicio.html', datosInicio=datosInicio)


@app.route('/inicio-editar', methods=["GET", "POST"])
def inicio_editar():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if session["user"]["rol_user"] != "Admin":
        return redirect(url_for('inicio'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM inicio WHERE id = 1")
    datosInicio = cursor.fetchone()

    if request.method == 'POST':
        dias = request.form.get('dias')
        horaInicio = request.form.get('horaInicio')
        horaFin = request.form.get('horaFin')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        correo = request.form.get('correo')

        logo = request.files.get('logo')

        static_path = os.path.abspath(os.path.join(app.root_path, '..', 'static'))

        if not os.path.exists(static_path):
            os.makedirs(static_path)
        
        if logo and logo.filename != '':
            ruta = os.path.join(static_path, 'logo.png')
            logo.save(ruta)

            cursor.execute(""" UPDATE inicio SET dias=%s, horaInicio=%s, horaFin=%s, telefono=%s, direccion=%s, correo=%s, logo=%s WHERE id = 1 """, 
            (dias, horaInicio, horaFin, telefono, direccion, correo, 'logo.png'))
        
        else:
            cursor.execute(""" UPDATE inicio SET dias=%s, horaInicio=%s, horaFin=%s, telefono=%s, direccion=%s, correo=%s WHERE id = 1 """, 
            (dias, horaInicio, horaFin, telefono, direccion, correo))
        
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('inicio'))

    cursor.close()
    conn.close()

    return render_template('modulos/inicio_editar.html', datosInicio=datosInicio)


# CONSULTORIOS ============================================
@app.route('/consultorios', methods=["GET", "POST"])
def consultorios():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if session["user"]["rol_user"] not in ["Admin", "Secretaria "]:
        return redirect(url_for('inicio'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Añadir consultorios
    if request.method == 'POST' and request.form.get('action') == 'agregar':
        consultorioNuevo = request.form["consultorio"]
        cursor.execute("INSERT INTO consultorios (consultorio) VALUES (%s)", (consultorioNuevo,))

        conn.commit()
        return redirect(url_for('consultorios'))

    # Editar consultorio
    if request.method == 'POST' and request.form.get('action') == 'editar':
        idC = request.form['idC']
        nombreC = request.form['consultorioEditar']

        cursor.execute("UPDATE consultorios SET consultorio = %s WHERE id = %s", (nombreC, idC))
        conn.commit()
        return redirect(url_for('consultorios'))
    
    # ELiminar consultorio
    if request.method == 'POST' and request.form.get('action') == 'eliminar':
        idC = request.form['idC']
        cursor.execute('DELETE FROM consultorios WHERE id = %s', (idC,))
        conn.commit()
        return redirect(url_for('consultorios'))

    # Lista de consultorios
    cursor.execute("SELECT * FROM consultorios")
    consultorios = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('modulos/consultorios.html', consultorios=consultorios)


# DOCTORES ============================================
@app.route('/doctores', methods=["GET", "POST"])
def doctores():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if session["user"]["rol_user"] not in ["Admin", "Secretaria "]:
        return redirect(url_for('inicio'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM consultorios")
    consultorios = cursor.fetchall()

    if request.method == 'POST':
        name_user = request.form['name_user']
        sexo = request.form['sexo']
        id_consultorio = request.form['id_consultorio']
        user = request.form['user']
        password_user = generate_password_hash(request.form['password_user'])
        rol_user = 'Doctor'
        estado = 0

        # Verificar que el usuario no exista
        cursor.execute('SELECT id_user FROM users WHERE user = %s', (user,))
        existe = cursor.fetchone()

        if existe:
            flash('El nombre de usuario ya esta registrado.', 'error')
            cursor.close()
            conn.close()

            return redirect(url_for('doctores'))
    
        # Insertar doctor
        cursor.execute('INSERT INTO users(name_user, password_user, rol_user, user, sexo, id_consultorio, estado) ' \
        'VALUES(%s,%s,%s,%s,%s,%s,%s)', (name_user, password_user, rol_user, user, sexo, id_consultorio, estado))

        conn.commit()

        ultimo_id = cursor.lastrowid

        cursor.execute('INSERT INTO doctores_horarios(id_doctor, horaInicio, horaFin) VALUES(%s,%s,%s)', (ultimo_id, 0, 0))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Doctor creado correctamente.', 'success')
        return redirect(url_for('doctores'))
    

    # Lista de doctores
    cursor.execute("select * from users u left join consultorios c on c.id = u.id_consultorio where u.rol_user = 'Doctor' and u.estado = 0")

    doctores = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('modulos/doctores.html', consultorios=consultorios, doctores=doctores)



if __name__ == '__main__':
    app.run(debug=True)
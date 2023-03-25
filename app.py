
from flask import Flask, render_template, request, session, redirect
import pymysql

users = {}
app = Flask(__name__)
app.secret_key = 'clave-secreta'

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'rentabika'

# Creación de la conexión a la base de datos
conn = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)

# Creación de la tabla si no existe
with conn.cursor() as cursor:
    cursor.execute('''CREATE TABLE IF NOT EXISTS alquileres
                      (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                      usuario VARCHAR(255),
                      bicicleta VARCHAR(255),
                      fecha_inicio TIMESTAMP,
                      fecha_fin TIMESTAMP,
                      costo INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios
                      (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                      nombre VARCHAR(255),
                      contrasena VARCHAR(255),
                      tipo_usuario VARCHAR(10))''')
    conn.commit()


def validar_login(username, password):
    # Se consulta la base de datos para verificar si el usuario y la contraseña son correctos
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        consulta = "SELECT * FROM usuarios WHERE nombre=%s AND contrasena=%s"
        cursor.execute(consulta, (username, password))
        resultado = cursor.fetchone()
        # Si se encuentra un resultado, se devuelve el tipo de usuario
        if resultado:
            return resultado['tipo_usuario']  # se modifica aquí el nombre de la columna
        else:
            return None
@app.route('/usuarios', methods=['GET'])
def mostrar_usuarios():
    # Obtención de los registros de la tabla
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM usuarios")
        rows = cursor.fetchall()

    return render_template('usuarios.html', rows=rows)



@app.route('/login', methods=['POST'])
def login():
    # Se obtienen los datos enviados por el formulario
    username = request.form['username']
    password = request.form['password']
    # Se verifica si el usuario y la contraseña son correctos
    tipo_usuario = validar_login(username, password)
    if tipo_usuario is not None:
        # Si son correctos, se inicia la sesión y se redirige a la página correspondiente
        session['username'] = username
        session['tipo'] = tipo_usuario
        if session['tipo'] == 'admin':
            return redirect('/admin')
        else:
            return redirect('/cliente')
    # Si no son correctos, se muestra un mensaje de error
    error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)


# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    # Se elimina la sesión y se redirige a la página de inicio de sesión
    session.pop('username', None)
    session.pop('tipo', None)
    return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Obtener los datos del formulario
        username = request.form['username']
        password = request.form['password']
        tipo_usuario = request.form.get('tipo_usuario') # Usar get() para evitar KeyError si no se selecciona un tipo de usuario
        
        # Insertar el nuevo usuario en la base de datos
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO usuarios (nombre, contrasena, tipo_usuario) VALUES (%s, %s, %s)", (username, password, tipo_usuario))
            conn.commit()
            
        return render_template('login.html')
    else:
        return render_template('signup.html')


@app.route('/')
def index():
    # Si el usuario ha iniciado sesión, se redirige a la página correspondiente
    if 'username' in session:
        if session['tipo'] == 'admin':
            return redirect('/admin')
        else:
            return redirect('/cliente')
    # Si el usuario no ha iniciado sesión, se muestra la página de inicio de sesión
    return render_template('login.html')

@app.route('/admin')
def admin():
    # Si el usuario no ha iniciado sesión o no es un administrador, se redirige a la página de inicio de sesión
    if 'username' not in session or session['tipo'] != 'admin':
        return redirect('/')
    # Si el usuario ha iniciado sesión y es un administrador, se muestra la página correspondiente
    return render_template('admin.html')


# Ruta para la página del cliente
@app.route('/cliente')
def cliente():
    # Si el usuario no ha iniciado sesión o no es un cliente, se redirige a la página de inicio de sesión
    if 'username' not in session or session['tipo'] != 'cliente':
        return redirect('/')
    # Si el usuario ha iniciado sesión y es un cliente, se muestra la página correspondiente
    return render_template('cliente.html')
@app.route('/alquileres', methods=['GET'])
def mostrar_alquileres():
    # Obtención de los registros de la tabla
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM alquileres")
        rows = cursor.fetchall()
    
    return render_template('alquileres.html', rows=rows)

@app.route('/alquileres/eliminar/<int:id>', methods=['POST'])
def eliminar_alquiler(id):
    # Eliminación del registro de la tabla
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM alquileres WHERE id = %s", (id,))
        conn.commit()

    return mostrar_alquileres()


@app.route('/alquileres/guardar', methods=['POST'])
def guardar_alquiler():
    # Se obtienen los datos del formulario
    usuario = request.form['usuario']
    bicicleta = request.form['bicicleta']
    fecha_inicio = request.form['fecha_inicio']
    hora_inicio = request.form['hora_inicio']
    fecha_fin = request.form['fecha_fin']
    hora_fin = request.form['hora_fin']
    costo = request.form['costo']

    # Se crea una fecha y hora completa a partir de las entradas separadas de fecha y hora
    fecha_hora_inicio = fecha_inicio + ' ' + hora_inicio
    fecha_hora_fin = fecha_fin + ' ' + hora_fin

    # Se inserta el nuevo alquiler en la base de datos
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO alquileres (usuario, bicicleta, fecha_inicio, fecha_fin, costo) VALUES (%s, %s, %s, %s, %s)",
                       (usuario, bicicleta, fecha_hora_inicio, fecha_hora_fin, costo))
        conn.commit()

    # Se redirige a la página de visualización de alquileres
    return 'Se registró el alquiler correctamente.'


if __name__ == '__main__':
    app.run(debug=True)

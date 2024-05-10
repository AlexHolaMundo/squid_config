import mysql.connector
import subprocess
from flask import Flask, redirect, url_for, session, render_template, request
from routes import prohibidas, usuarios, admitidas
from livereload import Server

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

ruta_archivo = '/etc/squid/squid.conf'

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306",
    database="squid")
prohibidas.configure_routes(app,conn)
usuarios.configure_routes(app, conn)
admitidas.configure_routes(app, conn)

# Ruta para mostrar el formulario de inicio de sesión
@app.route("/login", methods=["GET", "POST"])
def mostrar_formulario_login():
    if request.method == "POST":
        nombre_usa = request.form["nombre_usa"]
        password_usa = request.form["password_usa"]
        if verificar_credenciales(nombre_usa, password_usa):
            session["nombre_usa"] = nombre_usa
            return redirect(url_for("index"))
        else:
            return "Credenciales incorrectas. Inténtalo de nuevo."
    return render_template("login.html")

# Ruta para mostrar el formulario de Inicio
@app.route("/index")
def index():
    if "nombre_usa" in session:
        return render_template("home.html")
    else:
        return redirect(url_for("mostrar_formulario_login"))

# Ruta ACL
@app.route("/acl")
def acl():
    if "nombre_usa" in session:
        return render_template("acl.html")
    else:
        return redirect(url_for("mostrar_formulario_login"))

# Ruta Dias
@app.route("/dias")
def dias():
    if "nombre_usa" in session:
        return render_template("dias.html")
    else:
        return redirect(url_for("mostrar_formulario_dias"))

# Ruta Horas
@app.route("/horas")
def horas():
    if "nombre_usa" in session:
        return render_template("horas.html")
    else:
        return redirect(url_for("mostrar_formulario_horas"))

# Ruta Caches
@app.route("/cache")
def cache():
    if "nombre_usa" in session:
        return render_template("cache.html")
    else:
        return redirect(url_for("mostrar_formulario_caches"))

# Ruta Descargas
@app.route("/descargas")
def descargas():
    if "nombre_usa" in session:
        return render_template("descargas.html")
    else:
        return redirect(url_for("mostrar_formulario_descargas"))

# Ruta Puertos
@app.route("/puertos")
def puertos():
    if "nombre_usa" in session:
        return render_template("puerto.html")
    else:
        return redirect(url_for("mostrar_formulario_puerto"))

# Ruta Dns
@app.route("/dns")
def dns():
    if "nombre_usa" in session:
        return render_template("dns.html")
    else:
        return redirect(url_for("mostrar_formulario_dns"))

# Ruta Src
@app.route("/src")
def src():
    if "nombre_usa" in session:
        return render_template("src.html")
    else:
        return redirect(url_for("mostrar_formulario_src"))

@app.route('/configurar_acl', methods=['POST'])
def configurar_acl():
    try:
        # Obtener la IP y la máscara del formulario
        ip_acl = request.form['ip_acl']
        mascara_acl = request.form['mascara_acl']
        usuario_id = obtener_id_usuario(session["nombre_usa"])  # Obtener ID del usuario

        # Validar que la IP y la máscara sean válidas
        #ipaddress.IPv4Network(ip_acl+'/'+mascara_acl)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Acls (ip_acl, mascara_acl, fkid_usu) VALUES (%s, %s, %s)", (ip_acl, mascara_acl, usuario_id))
        conn.commit()

        # Generar la configuración de ACL de Squid
        configuracion_acl = f'''
acl nueva_red src {ip_acl}/{mascara_acl}
http_access allow nueva_red
'''
        # Agregar la nueva ACL al archivo de configuración de Squid
        with open(ruta_archivo, 'a') as archivo_configuracion:
            archivo_configuracion.write(configuracion_acl)

        # Reiniciar Squid para aplicar los cambios
        subprocess.run(['sudo', 'squid', '-k', 'reconfigure'])

        return 'ACL configurada correctamente y Squid reiniciado'
    except ValueError :
        return 'Error: La IP o la máscara no son válidas' + ValueError.__cause__

# Función para obtener el ID de un usuario dado su nombre de usuario
def obtener_id_usuario(nombre_usu):
    cursor = conn.cursor()
    sql = "SELECT id_usu FROM Usuarios WHERE nombre_usu = %s"
    valores = (nombre_usu,)
    cursor.execute(sql, valores)
    resultado = cursor.fetchone()
    if resultado:
        return resultado[0]
    else:
        return None

# Función para verificar las credenciales del usuario
def verificar_credenciales(nombre_usa, password_usa):
    cursor = conn.cursor()
    sql = "SELECT * FROM Usuarios WHERE nombre_usu = %s AND password_usu = %s"
    valores = (nombre_usa, password_usa)
    cursor.execute(sql, valores)
    usuario = cursor.fetchone()
    cursor.close()  # Cierra el cursor después de usarlo
    return usuario is not None



# Ruta para mostrar el formulario de departamento
@app.route('/departamentos')
def departamentos():
    return render_template('./departamento.html')

# Ruta para guardar un nuevo departamento en la base de datos
@app.route('/guardar_departamento', methods=['POST'])
def guardar_departamento():
    try:
        nombre_dep = request.form['nombre_dep']
        descripcion_dep = request.form['descripcion_dep']

        cursor = conn.cursor()
        cursor.execute("INSERT INTO Departamentos (nombre_dep, descripcion_dep) VALUES (%s, %s)", (nombre_dep, descripcion_dep))
        conn.commit()

        return 'Departamento guardado correctamente'
    except Exception as e:
        return f'Error al registrar el Departamento: {e}'

# Ruta para manejar la solicitud POST del inicio de sesión
@app.route("/login", methods=["POST"])
def iniciar_sesion():
    nombre_usa = request.form["nombre_usa"]
    password_usa = request.form["password_usa"]
    if verificar_credenciales(nombre_usa, password_usa):
        session["nombre_usa"] = nombre_usa
        return redirect(url_for("mostrar_formulario"))
    else:
        return "Credenciales incorrectas. Inténtalo de nuevo."

# Ruta para mostrar el formulario de registro de ACLs
@app.route("/")
def mostrar_formulario():
    # Verificar si el usuario ha iniciado sesión
    if "nombre_usa" in session:
        return render_template("home.html")
    else:
        return redirect(url_for("mostrar_formulario_login"))

# Ruta para cerrar la sesión del usuario
@app.route("/cerrar_sesion")
def cerrar_sesion():
    session.pop("nombre_usa", None)  # Elimina el elemento de la sesión correspondiente al usuario
    return redirect(url_for("mostrar_formulario_login"))

# Crear objeto Server de Livereload
server = Server(app.wsgi_app)

# Agregar rutas a observar para cambios
server.watch('**/*.html')
server.watch('**/*.css')
server.watch('**/*.js')
server.watch('**/*.py')
server.watch('**/*.txt')

if __name__ == '__main__':
    app.run(port=8081)

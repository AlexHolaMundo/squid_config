import subprocess
from flask import render_template, request

ruta_archivo = '/etc/squid/deny_social'
# Ruta para mostrar las páginas prohibidas
def configure_routes(app, conn):
    @app.route('/paginas_prohibidas')
    def paginas_prohibidas():
        return render_template('pgProhibidas.html')
    
    # Ruta para guardar un nuevo usuario en la base de datos
    @app.route('/guardar_pgProhibidas', methods=['POST'])
    def guardar_pgProhibidas():
        try:
            nombre_pgp = request.form['nombre_pgp']
            razon_pgp = request.form['razon_pgp']
            categoria_pgp = request.form["categoria_pgp"]
            dominio_pgp = request.form['dominio_pgp']
            cursor = conn.cursor()
            cursor.execute("INSERT INTO PaginasProhibidas (nombre_pgp, razon_pgp, categoria_pgp, dominio_pgp ) VALUES (%s, %s, %s, %s)", (nombre_pgp, razon_pgp, categoria_pgp, dominio_pgp))  # Corregido aquí
            conn.commit()

            # Agregar el sitio prohibido a la configuración de Squid
            guardar_pgProhibidas=  f''' {nombre_pgp}''' 
            subprocess.run(['sudo', 'squid', '-k', 'reconfigure'])
           # Agregar la nueva ACL al archivo de configuración de Squid
            with open(ruta_archivo, 'a') as archivo_configuracion:
                archivo_configuracion.write(guardar_pgProhibidas)
            
            # Reiniciar Squid para aplicar los cambios
            subprocess.run(['sudo', 'squid', '-k', 'reconfigure'])
            
            
            return 'Pagina guardada correctamente'
        except Exception as e:
            return f'Error al registrar la pagina: {e}'
        





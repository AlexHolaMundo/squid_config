import subprocess
from flask import render_template, request

ruta_archivo = '/etc/squid/access_social'
# Ruta para mostrar las páginas prohibidas
def configure_routes(app, conn):
    @app.route('/paginas_admitidas')
    def paginas_admitidas():
        return render_template('pgAdmitidas.html')
    
    # Ruta para guardar un nuevo usuario en la base de datos
    @app.route('/guardar_pgAdmitidas', methods=['POST'])
    def guardar_pgAdmitidas():
        try:
            nombre_pga = request.form['nombre_pga']
            razon_pga = request.form['razon_pga']
            categoria_pga = request.form["categoria_pga"]
            dominio_pga = request.form['dominio_pga']
            cursor = conn.cursor()
            cursor.execute("INSERT INTO PaginasAdmitidas (nombre_pga, razon_pga, categoria_pga, dominio_pga ) VALUES (%s, %s, %s, %s)", (nombre_pga, razon_pga, categoria_pga, dominio_pga))  # Corregido aquí
            conn.commit()

            # Agregar el sitio prohibido a la configuración de Squid
            guardar_pgAdmitidas=  f''' {nombre_pga}''' 
            subprocess.run(['sudo', 'squid', '-k', 'reconfigure'])
           # Agregar la nueva ACL al archivo de configuración de Squid
            with open(ruta_archivo, 'a') as archivo_configuracion:
                archivo_configuracion.write(guardar_pgAdmitidas)
            
            # Reiniciar Squid para aplicar los cambios
            subprocess.run(['sudo', 'squid', '-k', 'reconfigure'])
            
            
            return 'Pagina guardada correctamente'
        except Exception as e:
            return f'Error al registrar la pagina: {e}'
        





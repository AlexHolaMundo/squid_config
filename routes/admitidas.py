import subprocess
from flask import render_template, request

#ruta_archivo = '/etc/squid/dominios_admitidos'
ruta_archivo = '/etc/squid/dominios_admitidos'
ruta_archivo_squid = '/etc/squid/squid.conf'
linea_acl_filtro_prohibidas = 23
linea_acl_filtro_admitidas = 24
linea_http_filtro_prohibidas = 49
linea_http_filtro_admitidas = 50

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

            # Agregar el sitio admitido al archivo
            guardar_dominio =  f''' .{dominio_pga}'''

            with open(ruta_archivo, 'a') as archivo:
                archivo.write(guardar_dominio)

           # Agregar la nueva ACL al archivo de configuración de Squid
            with open(ruta_archivo_squid, 'r+') as archivo_configuracion:
                lineas = archivo_configuracion.readlines()

                if len(lineas) >= 2:
                    lineas[linea_acl_filtro_admitidas] = f'''acl filtro_admitidos dstdomain '/etc/squid/dominios_admitidos'\n'''
                    lineas[linea_http_filtro_admitidas] = f'''http_access allow filtro_admitidos\n'''
                archivo_configuracion.seek(0)
                archivo_configuracion.writelines(lineas)
                archivo_configuracion.truncate()

            # Reiniciar Squid para aplicar los cambios
            subprocess.run(['sudo', 'squid', '-k', 'reconfigure'])

            return 'Pagina guardada correctamente'
        except Exception as e:
            return f'Error al registrar la pagina: {e}'
